"""
CMFPlone setup handlers.
"""

from five.localsitemanager import make_objectmanager_site
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import setSite
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component import queryUtility

from zope.event import notify
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18n.locales import locales, LoadLocaleError
from zope.interface import implements

from Acquisition import aq_base, aq_get
from Products.StandardCacheManagers.AcceleratedHTTPCacheManager import \
     AcceleratedHTTPCacheManager
from Products.StandardCacheManagers.RAMCacheManager import \
     RAMCacheManager

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone import migrations as migs
from Products.CMFPlone.events import SiteManagerCreatedEvent
from Products.CMFPlone.Portal import member_indexhtml
from Products.ATContentTypes.lib import constraintypes
from Products.CMFQuickInstallerTool.interfaces import INonInstallable

from plone.i18n.normalizer.interfaces import IURLNormalizer
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY as CONTEXT_PORTLETS
from plone.app.portlets import portlets

from Products.CMFPlone.interfaces import IMigrationTool

class HiddenProducts(object):
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        return ['Archetypes', 'ATContentTypes', 'ATReferenceBrowserWidget',
                'CMFActionIcons', 'CMFCalendar', 'CMFDefault', 'CMFPlone',
                'CMFTopic', 'CMFUid', 'DCWorkflow', 'GroupUserFolder',
                'PasswordResetTool', 'wicked.at', 'kupu', 'PloneLanguageTool',
                'Kupu', 'CMFFormController', 'MimetypesRegistry',
                'PortalTransforms', 'CMFDiffTool', 'CMFEditions',
                'Products.ATReferenceBrowserWidget',
                'Products.CMFFormController',
                'Products.PloneLanguageTool',
               ]


class PloneGenerator:

    def installArchetypes(self, p):
        """QuickInstaller install of Archetypes and required dependencies."""
        qi = getToolByName(p, "portal_quickinstaller")
        qi.installProduct('CMFFormController', locked=1, hidden=1, forceProfile=True)
        qi.installProduct('MimetypesRegistry', locked=1, hidden=1, forceProfile=True)
        qi.installProduct('PortalTransforms', locked=1, hidden=1, forceProfile=True)
        qi.installProduct('Archetypes', locked=1, hidden=1,
            profile=u'Products.Archetypes:Archetypes')

    def installProducts(self, p):
        """QuickInstaller install of required Products"""
        qi = getToolByName(p, 'portal_quickinstaller')
        qi.installProduct('PlonePAS', locked=1, hidden=1, forceProfile=True)
        qi.installProduct('kupu', locked=0, forceProfile=True)
        qi.installProduct('CMFDiffTool', locked=0, forceProfile=True)
        qi.installProduct('CMFEditions', locked=0, forceProfile=True)
        qi.installProduct('PloneLanguageTool', locked=1, hidden=1, forceProfile=True)

    def addCacheHandlers(self, p):
        """ Add RAM and AcceleratedHTTP cache handlers """
        mgrs = [(AcceleratedHTTPCacheManager, 'HTTPCache'),
                (RAMCacheManager, 'RAMCache'),
                (RAMCacheManager, 'ResourceRegistryCache'),
                ]
        for mgr_class, mgr_id in mgrs:
            existing = p._getOb(mgr_id, None)
            if existing is None:
                p._setObject(mgr_id, mgr_class(mgr_id))
            else:
                unwrapped = aq_base(existing)
                if not isinstance(unwrapped, mgr_class):
                    p._delObject(mgr_id)
                    p._setObject(mgr_id, mgr_class(mgr_id))

    def addCacheForResourceRegistry(self, portal):
        ram_cache_id = 'ResourceRegistryCache'
        if ram_cache_id in portal.objectIds():
            cache = getattr(portal, ram_cache_id)
            settings = cache.getSettings()
            settings['max_age'] = 24*3600 # keep for up to 24 hours
            settings['request_vars'] = ('URL',)
            cache.manage_editProps('Cache for saved ResourceRegistry files', settings)
        reg = getToolByName(portal, 'portal_css', None)
        if reg is not None and getattr(aq_base(reg), 'ZCacheable_setManagerId', None) is not None:
            reg.ZCacheable_setManagerId(ram_cache_id)
            reg.ZCacheable_setEnabled(1)

        reg = getToolByName(portal, 'portal_kss', None)
        if reg is not None and getattr(aq_base(reg), 'ZCacheable_setManagerId', None) is not None:
            reg.ZCacheable_setManagerId(ram_cache_id)
            reg.ZCacheable_setEnabled(1)

        reg = getToolByName(portal, 'portal_javascripts', None)
        if reg is not None and getattr(aq_base(reg), 'ZCacheable_setManagerId', None) is not None:
            reg.ZCacheable_setManagerId(ram_cache_id)
            reg.ZCacheable_setEnabled(1)

    # XXX: This should all be done by custom setuphandlers
    def setupPortalContent(self, p):
        """
        Import default plone content
        """
        existing = p.objectIds()
        
        wftool = getToolByName(p, "portal_workflow")

        # Figure out the current user preferred language
        language = None
        locale = None
        request = getattr(p, 'REQUEST', None)
        if request is not None:
            pl = IUserPreferredLanguages(request)
            if pl is not None:
                languages = pl.getPreferredLanguages()
                for httplang in languages:
                    parts = (httplang.split('-') + [None, None])[:3]
                    try:
                        locale = locales.getLocale(*parts)
                        break
                    except LoadLocaleError:
                        # Just try the next combination
                        pass
                if len(languages) > 0:
                    language = languages[0]

        # Set the default language of the portal
        if language is not None and locale is not None:
            localeid = locale.getLocaleID()
            base_language = locale.id.language

            # If we get a territory, we enable the combined language codes
            use_combined = False
            if locale.id.territory:
                use_combined = True

            # As we have a sensible language code set now, we disable the
            # start neutral functionality
            tool = getToolByName(p, "portal_languages")
            pprop = getToolByName(p, "portal_properties")
            sheet = pprop.site_properties 

            tool.manage_setLanguageSettings(language,
                [language],
                setUseCombinedLanguageCodes=use_combined,
                startNeutral=False)

            # Enable visible_ids for non-latin scripts

            # See if we have an url normalizer
            normalizer = queryUtility(IURLNormalizer, name=localeid)
            if normalizer is None:
                normalizer = queryUtility(IURLNormalizer, name=base_language)

            # If we get a script other than Latn we enable visible_ids
            if locale.id.script is not None:
                if locale.id.script.lower() != 'latn':
                    sheet.visible_ids = True

            # If we have a normalizer it is safe to disable the visible ids
            if normalizer is not None:
                sheet.visible_ids = False

        # Special handling of the front-page, as we want to translate it
        if 'front-page' in existing:
            fp = p['front-page']
            if wftool.getInfoFor(fp, 'review_state') != 'published':
                wftool.doActionFor(fp, 'publish')

            # Show off presentation mode
            fp.setPresentation(True)

            # Mark as fully created
            fp.unmarkCreationFlag()

            if language is not None:
                util = queryUtility(ITranslationDomain, 'plonefrontpage')
                if util is not None:
                    front_title = util.translate(u'front-title',
                                       target_language=language,
                                       default="Welcome to Plone")
                    front_desc = util.translate(u'front-description',
                                       target_language=language,
                                       default="Congratulations! You have successfully installed Plone.")
                    front_text = util.translate(u'front-text',
                                       target_language=language)
                    fp.setLanguage(language)
                    fp.setTitle(front_title)
                    fp.setDescription(front_desc)
                    if front_text <> u'front-text':
                        fp.setText(front_text)

        # News topic
        if 'news' not in existing:
            news_title = 'News'
            news_desc = 'Site News'
            if language is not None:
                util = queryUtility(ITranslationDomain, 'plonefrontpage')
                if util is not None:
                    news_title = util.translate(u'news-title',
                                           target_language=language,
                                           default='News')
                    news_desc = util.translate(u'news-description',
                                          target_language=language,
                                          default='Site News')

            _createObjectByType('Large Plone Folder', p, id='news',
                                title=news_title, description=news_desc)
            _createObjectByType('Topic', p.news, id='aggregator',
                                title=news_title, description=news_desc)

            folder = p.news
            folder.setConstrainTypesMode(constraintypes.ENABLED)
            folder.setLocallyAllowedTypes(['News Item'])
            folder.setImmediatelyAddableTypes(['News Item'])
            folder.setDefaultPage('aggregator')
            folder.unmarkCreationFlag()
            if language is not None:
                folder.setLanguage(language)

            if wftool.getInfoFor(folder, 'review_state') != 'published':
                wftool.doActionFor(folder, 'publish')

            topic = p.news.aggregator
            if language is not None:
                topic.setLanguage(language)
            type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
            type_crit.setValue('News Item')
            sort_crit = topic.addCriterion('created','ATSortCriterion')
            state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
            state_crit.setValue('published')
            topic.setSortCriterion('effective', True)
            topic.setLayout('folder_summary_view')
            topic.unmarkCreationFlag()

            if wftool.getInfoFor(topic, 'review_state') != 'published':
                wftool.doActionFor(topic, 'publish')

        # Events topic
        if 'events' not in existing:
            events_title = 'Events'
            events_desc = 'Site Events'
            if language is not None:
                util = queryUtility(ITranslationDomain, 'plonefrontpage')
                if util is not None:
                    events_title = util.translate(u'events-title',
                                           target_language=language,
                                           default='Events')
                    events_desc = util.translate(u'events-description',
                                          target_language=language,
                                          default='Site Events')

            _createObjectByType('Large Plone Folder', p, id='events',
                                title=events_title, description=events_desc)
            _createObjectByType('Topic', p.events, id='aggregator',
                                title=events_title, description=events_desc)
            folder = p.events
            folder.setConstrainTypesMode(constraintypes.ENABLED)
            folder.setLocallyAllowedTypes(['Event'])
            folder.setImmediatelyAddableTypes(['Event'])
            folder.setDefaultPage('aggregator')
            folder.unmarkCreationFlag()
            if language is not None:
                folder.setLanguage(language)
            
            if wftool.getInfoFor(folder, 'review_state') != 'published':
                wftool.doActionFor(folder, 'publish')
            
            topic = folder.aggregator
            topic.unmarkCreationFlag()
            if language is not None:
                topic.setLanguage(language)
            type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
            type_crit.setValue('Event')
            sort_crit = topic.addCriterion('start','ATSortCriterion')
            state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
            state_crit.setValue('published')
            date_crit = topic.addCriterion('start', 'ATFriendlyDateCriteria')
            # Set date reference to now
            date_crit.setValue(0)
            # Only take events in the future
            date_crit.setDateRange('+') # This is irrelevant when the date is now
            date_crit.setOperation('more')
        else:
            topic = p.events
            
        if wftool.getInfoFor(topic, 'review_state') != 'published':
            wftool.doActionFor(topic, 'publish')

        # Previous events subtopic
        if 'previous' not in topic.objectIds():
            prev_events_title = 'Past Events'
            prev_events_desc = 'Events which have already happened.'
            if language is not None:
                util = queryUtility(ITranslationDomain, 'plonefrontpage')
                if util is not None:
                    prev_events_title = util.translate(u'prev-events-title',
                                           target_language=language,
                                           default='Past Events')
                    prev_events_desc = util.translate(u'prev-events-description',
                                          target_language=language,
                                          default='Events which have already happened.')
            
            _createObjectByType('Topic', topic, id='previous',
                                title=prev_events_title,
                                description=prev_events_desc)
            topic = topic.previous
            if language is not None:
                topic.setLanguage(language)
            topic.setAcquireCriteria(True)
            topic.unmarkCreationFlag()
            sort_crit = topic.addCriterion('start','ATSortCriterion')
            sort_crit.setReversed(True)
            date_crit = topic.addCriterion('start','ATFriendlyDateCriteria')
            # Set date reference to now
            date_crit.setValue(0)
            # Only take events in the past
            date_crit.setDateRange('-') # This is irrelevant when the date is now
            date_crit.setOperation('less')
            
            if wftool.getInfoFor(topic, 'review_state') != 'published':
                wftool.doActionFor(topic, 'publish')

        if 'Members' in existing:
            # configure Members folder (already added by the content import)
            members_title = 'Users'
            members_desc = "Container for users' home directories"
            if language is not None:
                util = queryUtility(ITranslationDomain, 'plonefrontpage')
                if util is not None:
                    members_title = util.translate(u'members-title',
                                           target_language=language,
                                           default='Users')
                    members_desc = util.translate(u'members-description',
                                          target_language=language,
                                          default="Container for users' home directories")

            members = getattr(p , 'Members')
            members.setTitle(members_title)
            members.setDescription(members_desc)
            members.unmarkCreationFlag()
            if language is not None:
                members.setLanguage(language)
            members.reindexObject()
            
            if wftool.getInfoFor(members, 'review_state') != 'published':
                wftool.doActionFor(members, 'publish')
            
            # Disable portlets here
            rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=p)
            portletAssignments = getMultiAdapter((members, rightColumn,), ILocalPortletAssignmentManager)
            portletAssignments.setBlacklistStatus(CONTEXT_PORTLETS, True)
            
            # add index_html to Members area
            if 'index_html' not in members.objectIds():
                addPy = members.manage_addProduct['PythonScripts'].manage_addPythonScript
                addPy('index_html')
                index_html = getattr(members, 'index_html')
                index_html.write(member_indexhtml)
                index_html.ZPythonScript_setTitle('User Search')

    def performMigrationActions(self, p):
        """
        Perform any necessary migration steps.
        """
        mt = queryUtility(IMigrationTool)
        mt.setInstanceVersion(mt.getFileSystemVersion())

    def enableSyndication(self, portal, out):
        syn = getToolByName(portal, 'portal_syndication', None)
        if syn is not None:
            syn.editProperties(isAllowed=True)
            cat = getToolByName(portal, 'portal_catalog', None)
            if cat is not None:
                topics = cat(portal_type='Topic')
                for b in topics:
                    topic = b.getObject()
                    # If syndication is already enabled then another nasty string
                    # exception gets raised in CMFDefault
                    if topic is not None and not syn.isSyndicationAllowed(topic):
                        syn.enableSyndication(topic)
                        out.append('Enabled syndication on %s'%b.getPath())

    def enableSite(self, portal):
        """
        Make the portal a Zope3 site and create a site manager.
        """
        if not ISite.providedBy(portal):
            make_objectmanager_site(portal)
        # The following event is primarily useful for setting the site hooks
        # during test runs.
        notify(SiteManagerCreatedEvent(portal))

    def assignTitles(self, portal, out):
        titles={'portal_actions':'Contains custom tabs and buttons',
         'portal_membership':'Handles membership policies',
         'portal_memberdata':'Handles the available properties on members',
         'portal_undo':'Defines actions and functionality related to undo',
         'portal_types':'Controls the available content types in your portal',
         'plone_utils':'Various utility methods',
         'portal_metadata':'Controls metadata like keywords, copyrights, etc',
         'portal_migration':'Upgrades to newer Plone versions',
         'portal_registration':'Handles registration of new users',
         'portal_skins':'Controls skin behaviour (search order etc)',
         'portal_syndication':'Generates RSS for folders',
         'portal_workflow':'Contains workflow definitions for your portal',
         'portal_url':'Methods to anchor you to the root of your Plone site',
         'portal_discussion':'Controls how discussions are stored',
         'portal_catalog':'Indexes all content in the site',
         'portal_factory':'Responsible for the creation of content objects',
         'portal_calendar':'Controls how events are shown',
         'portal_quickinstaller':'Allows to install/uninstall products',
         'portal_interface':'Allows to query object interfaces',
         'portal_actionicons':'Associates actions with icons',
         'portal_groupdata':'Handles properties on groups',
         'portal_groups':'Handles group related functionality',
         'translation_service': 'Provides access to the translation machinery',
         'mimetypes_registry': 'MIME types recognized by Plone',
         'portal_transforms': 'Handles data conversion between MIME types',
         }
    
        for oid in portal.objectIds():
            title=titles.get(oid, None)
            if title:
                setattr(aq_get(portal, oid), 'title', title)
        out.append('Assigned titles to portal tools.')

    def addDefaultPortlets(self, portal):
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=portal)
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=portal)
        
        left = getMultiAdapter((portal, leftColumn,), IPortletAssignmentMapping, context=portal)
        right = getMultiAdapter((portal, rightColumn,), IPortletAssignmentMapping, context=portal)
        
        if u'navigation' not in left:
            left[u'navigation'] = portlets.navigation.Assignment()
        if u'login' not in left:
            left[u'login'] = portlets.login.Assignment()
        
        if u'review' not in right:
            right[u'review'] = portlets.review.Assignment(count=5)
        if u'news' not in right:
            right[u'news'] = portlets.news.Assignment(count=5)
        if u'events' not in right:
            right[u'events'] = portlets.events.Assignment(count=5)
        if u'calendar' not in right:
            right[u'calendar'] = portlets.calendar.Assignment()

def importSite(context):
    """
    Import site settings.
    """
    site = context.getSite()
    gen = PloneGenerator()
    gen.enableSite(site)
    setSite(site)

def importArchetypes(context):
    """
    Install Archetypes and it's dependencies.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('plone_archetypes.txt') is None:
        return
    site = context.getSite()
    gen = PloneGenerator()
    gen.installArchetypes(site)

def importVarious(context):
    """
    Import various settings.

    Provisional handler that does initialization that is not yet taken
    care of by other handlers.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('plone_various.txt') is None:
        return
    site = context.getSite()
    gen = PloneGenerator()
    gen.installProducts(site)
    gen.addCacheHandlers(site)
    gen.addCacheForResourceRegistry(site)

def importFinalSteps(context):
    """
    Final Plone import steps.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('plone-final.txt') is None:
        return
    out = []
    site = context.getSite()
    pprop = getToolByName(site, 'portal_properties')
    pmembership = getToolByName(site, 'portal_membership')
    gen = PloneGenerator()
    gen.addDefaultPortlets(site)
    gen.performMigrationActions(site)
    gen.enableSyndication(site, out)
    gen.assignTitles(site, out)
    site.manage_permission('Add portal member', roles=['Manager','Owner'], acquire=0)
    pprop.site_properties.allowAnonymousViewAbout = False
    pmembership.memberareaCreationFlag = False

def importContent(context):
    """
    Final Plone content import step.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('plone-content.txt') is None:
        return
    out = []
    site = context.getSite()
    gen = PloneGenerator()
    gen.setupPortalContent(site)

def updateWorkflowRoleMappings(context):
    """
    If an extension profile (such as the testfixture one) switches default,
    workflows, this import handler will make sure object security works
    properly.
    """
    site = context.getSite()
    portal_workflow = getToolByName(site, 'portal_workflow')
    portal_workflow.updateRoleMappings()