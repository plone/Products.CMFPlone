"""
CMFPlone setup handlers.
"""

from borg.localrole.utils import replace_local_role_manager
from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import IPortletManager

from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.locales import locales
from zope.interface import implements

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.lib import constraintypes
from Products.CMFDefault.utils import bodyfinder
from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from Products.StandardCacheManagers.AcceleratedHTTPCacheManager \
    import AcceleratedHTTPCacheManager
from Products.StandardCacheManagers.RAMCacheManager import RAMCacheManager

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.interfaces import IMigrationTool
from Products.CMFPlone.Portal import member_indexhtml


class HiddenProducts(object):
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        return [
            'Archetypes', 'Products.Archetypes',
            'ATContentTypes', 'Products.ATContentTypes',
            'ATReferenceBrowserWidget', 'Products.ATReferenceBrowserWidget',
            'archetypes.referencebrowserwidget',
            'CMFActionIcons', 'Products.CMFActionIcons',
            'CMFCalendar', 'Products.CMFCalendar',
            'CMFDefault', 'Products.CMFDefault',
            'CMFPlone', 'Products.CMFPlone', 'Products.CMFPlone.migrations',
            'CMFTopic', 'Products.CMFTopic',
            'CMFUid', 'Products.CMFUid',
            'DCWorkflow', 'Products.DCWorkflow',
            'PasswordResetTool', 'Products.PasswordResetTool',
            'PlonePAS', 'Products.PlonePAS',
            'wicked.at',
            'PloneLanguageTool', 'Products.PloneLanguageTool',
            'TinyMCE', 'Products.TinyMCE',
            'CMFFormController', 'Products.CMFFormController',
            'MimetypesRegistry', 'Products.MimetypesRegistry',
            'PortalTransforms', 'Products.PortalTransforms',
            'CMFDiffTool', 'Products.CMFDiffTool',
            'CMFEditions', 'Products.CMFEditions',
            'Products.NuPlone',
            'plone.portlet.static',
            'plone.portlet.collection',
            'borg.localrole',
            'plone.keyring',
            'plone.protect',
            'plone.app.jquery',
            'plone.app.jquerytools',
            'plone.app.blob',
            'plone.app.discussion',
            'plone.app.folder',
            'plone.app.imaging',
            'plone.outputfilters',
            'plonetheme.sunburst',
            'plone.app.registry',
            'plone.app.search',
            'plone.app.z3cform',

            ]


def addCacheHandlers(portal):
    """ Add RAM and AcceleratedHTTP cache handlers """
    mgrs = [(AcceleratedHTTPCacheManager, 'HTTPCache'),
            (RAMCacheManager, 'RAMCache'),
            (RAMCacheManager, 'ResourceRegistryCache'),
            ]
    for mgr_class, mgr_id in mgrs:
        existing = portal.get(mgr_id, None)
        if existing is None:
            portal[mgr_id] = mgr_class(mgr_id)
        else:
            unwrapped = aq_base(existing)
            if not isinstance(unwrapped, mgr_class):
                del portal[mgr_id]
                portal[mgr_id] = mgr_class(mgr_id)


def addCacheForResourceRegistry(portal):
    ram_cache_id = 'ResourceRegistryCache'
    if ram_cache_id in portal:
        cache = getattr(portal, ram_cache_id)
        settings = cache.getSettings()
        settings['max_age'] = 24 * 3600  # keep for up to 24 hours
        settings['request_vars'] = ('URL', )
        cache.manage_editProps('Cache for saved ResourceRegistry files',
                               settings)
    reg = getToolByName(portal, 'portal_css', None)
    if reg is not None \
            and getattr(aq_base(reg), 'ZCacheable_setManagerId', None) \
                is not None:
        reg.ZCacheable_setManagerId(ram_cache_id)
        reg.ZCacheable_setEnabled(1)

    reg = getToolByName(portal, 'portal_javascripts', None)
    if reg is not None \
            and getattr(aq_base(reg), 'ZCacheable_setManagerId', None) \
                is not None:
        reg.ZCacheable_setManagerId(ram_cache_id)
        reg.ZCacheable_setEnabled(1)


def setupPortalContent(p):
    """
    Import default plone content
    """
    existing = p.keys()
    wftool = getToolByName(p, "portal_workflow")

    language = p.Language()
    parts = (language.split('-') + [None, None])[:3]
    locale = locales.getLocale(*parts)
    target_language = base_language = locale.id.language

    # If we get a territory, we enable the combined language codes
    use_combined = False
    if locale.id.territory:
        use_combined = True
        target_language += '_' + locale.id.territory

    # As we have a sensible language code set now, we disable the
    # start neutral functionality
    tool = getToolByName(p, "portal_languages")
    pprop = getToolByName(p, "portal_properties")
    sheet = pprop.site_properties

    tool.manage_setLanguageSettings(language,
        [language],
        setUseCombinedLanguageCodes=use_combined,
        startNeutral=False)

    # Set the first day of the week, defaulting to Sunday, as the
    # locale data doesn't provide a value for English. European
    # languages / countries have an entry of Monday, though.
    calendar = getToolByName(p, "portal_calendar", None)
    if calendar is not None:
        first = 6
        gregorian = locale.dates.calendars.get(u'gregorian', None)
        if gregorian is not None:
            first = gregorian.week.get('firstDay', None)
            # on the locale object we have: mon : 1 ... sun : 7
            # on the calendar tool we have: mon : 0 ... sun : 6
            if first is not None:
                first = first - 1

        calendar.firstweekday = first

    # Enable visible_ids for non-latin scripts

    # See if we have an url normalizer
    normalizer = queryUtility(IURLNormalizer, name=target_language)
    if normalizer is None:
        normalizer = queryUtility(IURLNormalizer, name=base_language)

    # If we get a script other than Latn we enable visible_ids
    if locale.id.script is not None:
        if locale.id.script.lower() != 'latn':
            sheet.visible_ids = True

    # If we have a normalizer it is safe to disable the visible ids
    if normalizer is not None:
        sheet.visible_ids = False

    request = getattr(p, 'REQUEST', None)
    # The front-page
    if 'front-page' not in existing:
        front_title = u'Welcome to Plone'
        front_desc = u'Congratulations! You have successfully installed Plone.'
        front_text = None
        _createObjectByType('Document', p, id='front-page',
                            title=front_title, description=front_desc)
        fp = p['front-page']
        if wftool.getInfoFor(fp, 'review_state') != 'published':
            wftool.doActionFor(fp, 'publish')

        if base_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                front_title = util.translate(
                                    u'front-title',
                                    target_language=target_language,
                                    default="Welcome to Plone")
                front_desc = util.translate(
                    u'front-description',
                    target_language=target_language,
                    default="Congratulations! You have successfully installed "
                            "Plone.")
                translated_text = util.translate(u'front-text',
                                   target_language=target_language)
                if translated_text != u'front-text':
                    front_text = translated_text

        if front_text is None and request is not None:
            view = queryMultiAdapter((p, request),
                name='plone-frontpage-setup')
            if view is not None:
                front_text = bodyfinder(view.index()).strip()

        fp.setTitle(front_title)
        fp.setDescription(front_desc)
        fp.setLanguage(language)
        fp.setText(front_text, mimetype='text/html')

        # Show off presentation mode
        if hasattr(fp, 'setPresentation'):
            fp.setPresentation(True)

        # Mark as fully created
        fp.unmarkCreationFlag()

        p.setDefaultPage('front-page')
        fp.reindexObject()

    # News topic
    if 'news' not in existing:
        news_title = 'News'
        news_desc = 'Site News'
        if base_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                news_title = util.translate(u'news-title',
                                       target_language=target_language,
                                       default='News')
                news_desc = util.translate(u'news-description',
                                      target_language=target_language,
                                      default='Site News')

        _createObjectByType('Folder', p, id='news',
                            title=news_title, description=news_desc)
        _createObjectByType('Collection', p.news, id='aggregator',
                            title=news_title, description=news_desc)

        folder = p.news
        folder.setConstrainTypesMode(constraintypes.ENABLED)
        folder.setLocallyAllowedTypes(['News Item'])
        folder.setImmediatelyAddableTypes(['News Item'])
        folder.setDefaultPage('aggregator')
        folder.unmarkCreationFlag()
        folder.setLanguage(language)

        if wftool.getInfoFor(folder, 'review_state') != 'published':
            wftool.doActionFor(folder, 'publish')

        topic = p.news.aggregator
        topic.setLanguage(language)

        query = [{'i': 'portal_type',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['News Item']},
                 {'i': 'review_state',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['published']}]
        topic.setQuery(query)

        topic.setSort_on('effective')
        topic.setSort_reversed(True)
        topic.setLayout('folder_summary_view')
        topic.unmarkCreationFlag()

        if wftool.getInfoFor(topic, 'review_state') != 'published':
            wftool.doActionFor(topic, 'publish')

    # Events topic
    if 'events' not in existing:
        events_title = 'Events'
        events_desc = 'Site Events'
        if base_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                events_title = util.translate(u'events-title',
                                       target_language=target_language,
                                       default='Events')
                events_desc = util.translate(u'events-description',
                                      target_language=target_language,
                                      default='Site Events')

        _createObjectByType('Folder', p, id='events',
                            title=events_title, description=events_desc)
        _createObjectByType('Collection', p.events, id='aggregator',
                            title=events_title, description=events_desc)
        folder = p.events
        folder.setConstrainTypesMode(constraintypes.ENABLED)
        folder.setLocallyAllowedTypes(['Event'])
        folder.setImmediatelyAddableTypes(['Event'])
        folder.setDefaultPage('aggregator')
        folder.unmarkCreationFlag()
        folder.setLanguage(language)

        if wftool.getInfoFor(folder, 'review_state') != 'published':
            wftool.doActionFor(folder, 'publish')

        topic = folder.aggregator
        topic.unmarkCreationFlag()
        topic.setLanguage(language)

        query = [{'i': 'portal_type',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['Event']},
                 {'i': 'start',
                  'o': 'plone.app.querystring.operation.date.afterToday',
                  'v': ''},
                 {'i': 'review_state',
                  'o': 'plone.app.querystring.operation.selection.is',
                  'v': ['published']}]
        topic.setQuery(query)
        topic.setSort_on('start')
    else:
        topic = p.events

    if wftool.getInfoFor(topic, 'review_state') != 'published':
        wftool.doActionFor(topic, 'publish')

    # configure Members folder
    members_title = 'Users'
    members_desc = "Site Users"
    if 'Members' not in existing:
        _createObjectByType('Folder', p, id='Members',
                            title=members_title, description=members_desc)

    if 'Members' in p.keys():
        if base_language != 'en':
            util = queryUtility(ITranslationDomain, 'plonefrontpage')
            if util is not None:
                members_title = util.translate(u'members-title',
                                       target_language=target_language,
                                       default='Users')
                members_desc = util.translate(u'members-description',
                                      target_language=target_language,
                                      default="Site Users")

        members = getattr(p, 'Members')
        members.setTitle(members_title)
        members.setDescription(members_desc)
        members.unmarkCreationFlag()
        members.setLanguage(language)
        members.reindexObject()

        if wftool.getInfoFor(members, 'review_state') != 'published':
            wftool.doActionFor(members, 'publish')

        # add index_html to Members area
        if 'index_html' not in members.objectIds():
            addPy = members.manage_addProduct['PythonScripts'] \
                        .manage_addPythonScript
            addPy('index_html')
            index_html = getattr(members, 'index_html')
            index_html.write(member_indexhtml)
            index_html.ZPythonScript_setTitle('User Search')

        # Block all right column portlets by default
        manager = queryUtility(IPortletManager, name='plone.rightcolumn')
        if manager is not None:
            assignable = queryMultiAdapter(
                            (members, manager),
                            ILocalPortletAssignmentManager)
            assignable.setBlacklistStatus('context', True)
            assignable.setBlacklistStatus('group', True)
            assignable.setBlacklistStatus('content_type', True)


def setProfileVersion(portal):
    """
    Set profile version.
    """
    mt = queryUtility(IMigrationTool)
    mt.setInstanceVersion(mt.getFileSystemVersion())
    setup = getToolByName(portal, 'portal_setup')
    version = setup.getVersionForProfile(_DEFAULT_PROFILE)
    setup.setLastVersionForProfile(_DEFAULT_PROFILE, version)


def assignTitles(portal):
    titles = {
     'acl_users': 'User / Group storage and authentication settings',
     'archetype_tool': 'Archetypes specific settings',
     'caching_policy_manager': 'Settings related to proxy caching',
     'content_type_registry': 'MIME type settings',
     'error_log': 'Error and exceptions log viewer',
     'MailHost': 'Mail server settings for outgoing mail',
     'mimetypes_registry': 'MIME types recognized by Plone',
     'plone_utils': 'Various utility methods',
     'portal_actionicons': 'Associates actions with icons',
     'portal_actions': 'Contains custom tabs and buttons',
     'portal_atct': 'Collection and image scales settings',
     'portal_calendar': 'Controls how events are shown',
     'portal_catalog': 'Indexes all content in the site',
     'portal_controlpanel': 'Registry of control panel screen',
     'portal_css': 'Registry of CSS files',
     'portal_diff': 'Settings for content version comparisions',
     'portal_discussion': 'Controls how discussions are stored',
     'portal_factory': 'Responsible for the creation of content objects',
     'portal_form_controller': 'Registration of form and validation chains',
     'portal_groupdata': 'Handles properties on groups',
     'portal_groups': 'Handles group related functionality',
     'portal_interface': 'Allows to query object interfaces',
     'portal_javascripts': 'Registry of JavaScript files',
     'portal_languages': 'Language specific settings',
     'portal_membership': 'Handles membership policies',
     'portal_memberdata': 'Handles the available properties on members',
     'portal_metadata': 'Controls metadata like keywords, copyrights, etc',
     'portal_migration': 'Upgrades to newer Plone versions',
     'portal_password_reset': 'Handles password retention policy',
     'portal_properties': 'General settings registry',
     'portal_quickinstaller': 'Allows to install/uninstall products',
     'portal_registration': 'Handles registration of new users',
     'portal_setup': 'Add-on and configuration management',
     'portal_skins': 'Controls skin behaviour (search order etc)',
     'portal_transforms': 'Handles data conversion between MIME types',
     'portal_types': 'Controls the available content types in your portal',
     'portal_undo': 'Defines actions and functionality related to undo',
     'portal_url': 'Methods to anchor you to the root of your Plone site',
     'portal_view_customizations': 'Template customizations',
     'portal_workflow': 'Contains workflow definitions for your portal',
     'reference_catalog': 'Catalog of content references',
     'translation_service': 'Provides access to the translation machinery',
     'uid_catalog': 'Catalog of unique content identifiers',
     }
    for oid, obj in portal.items():
        title = titles.get(oid, None)
        if title:
            setattr(aq_base(obj), 'title', title)


def importFinalSteps(context):
    """
    Final Plone import steps.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('plone-final.txt') is None:
        return
    site = context.getSite()
    setProfileVersion(site)

    # Install our dependencies
    st = getToolByName(site, "portal_setup")
    st.runAllImportStepsFromProfile("profile-Products.CMFPlone:dependencies")

    assignTitles(site)
    replace_local_role_manager(site)
    addCacheHandlers(site)
    addCacheForResourceRegistry(site)


def importContent(context):
    """
    Final Plone content import step.
    """
    # Only run step if a flag file is present
    if context.readDataFile('plone-content.txt') is None:
        return
    site = context.getSite()
    setupPortalContent(site)


def updateWorkflowRoleMappings(context):
    """
    If an extension profile (such as the testfixture one) switches default,
    workflows, this import handler will make sure object security works
    properly.
    """
    # Only run step if a flag file is present
    if context.readDataFile('plone-update-workflow-rolemap.txt') is None:
        return
    site = context.getSite()
    portal_workflow = getToolByName(site, 'portal_workflow')
    portal_workflow.updateRoleMappings()
