"""
CMFPlone setup handlers.
"""

from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component import queryUtility

from zope.component.globalregistry import base
from zope.component.persistentregistry import PersistentComponents
from zope.event import notify
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.interfaces import IUserPreferredLanguages
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
from Products.CMFQuickInstallerTool.interfaces import INonInstallable
from Products.Five.component import enableSite
from Products.Five.component.interfaces import IObjectManagerSite

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY as CONTEXT_PORTLETS
from plone.app.portlets import portlets


class HiddenProducts(object):
    implements(INonInstallable)

    def getNonInstallableProducts(self):
        return ['Archetypes', 'ATContentTypes', 'ATReferenceBrowserWidget',
                'CMFActionIcons', 'CMFCalendar', 'CMFDefault',
                'CMFTopic', 'CMFUid', 'DCWorkflow', 'GroupUserFolder',
                'PasswordResetTool'
                # TODO: These are added by installing Archetypes through QI,
                # which shouldn't happen at all anymore. We don't add those
                # to this list right now, as we don't want to get any annoying
                # "removed from Products folder" messages.
                # 'CMFFormController', 'MimetypesRegistry', 'PortalTransforms'
               ]


class PloneGenerator:

    def installProducts(self, p):
        """QuickInstaller install of required Products"""
        # XXX The product installations should be done by a GenericSetup
        # handler
        qi = getToolByName(p, 'portal_quickinstaller')
        qi.installProduct('Archetypes', locked=1, hidden=1)
        qi.installProduct('PlonePAS', locked=1, hidden=1, forceProfile=True)
        qi.installProduct('CMFPlacefulWorkflow', locked=0)
        qi.installProduct('kupu', locked=0)

        # The following two products are "installed" based on a GenericSetup
        # extension profile by CMFQuickInstallerTool
        qi.installProduct('CMFDiffTool', locked=0, forceProfile=True)
        qi.installProduct('CMFEditions', locked=0, forceProfile=True)

    def addCacheHandlers(self, p):
        """ Add RAM and AcceleratedHTTP cache handlers """
        mgrs = [(AcceleratedHTTPCacheManager, 'HTTPCache'),
                (RAMCacheManager, 'RAMCache'),
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

    # XXX: This should all be done by custom setuphandlers
    def setupPortalContent(self, p):
        """
        Import default plone content
        """
        existing = p.objectIds()

        # Special handling of the front-page, as we want to translate it into
        # the current user preferred language
        if 'front-page' in existing:
            fp = p['front-page']
            pl = IUserPreferredLanguages(p.REQUEST)
            if pl is not None:
                languages = pl.getPreferredLanguages()
                if len(languages) > 0:
                    language = languages[0]
                    util = queryUtility(ITranslationDomain, 'plonefrontpage')
                    if util is not None:
                        title = util.translate(u'title',
                                               target_language=language)
                        desc = util.translate(u'description',
                                              target_language=language)
                        text = util.translate(u'text',
                                              target_language=language)
                        if title <> u'title' and text <> u'text':
                            fp.setLanguage(language)
                            fp.setTitle(title)
                            fp.setDescription(desc)
                            fp.setText(text)

        # News topic
        if 'news' not in existing:
            _createObjectByType('Topic', p, id='news', title='News',
                                description='Site News')
            topic = p.news
            type_crit = topic.addCriterion('Type','ATPortalTypeCriterion')
            type_crit.setValue('News Item')
            sort_crit = topic.addCriterion('created','ATSortCriterion')
            state_crit = topic.addCriterion('review_state', 'ATSimpleStringCriterion')
            state_crit.setValue('published')
            topic.setSortCriterion('effective', True)
            topic.setLayout('folder_summary_view')

        # Events topic
        if 'events' not in existing:
            _createObjectByType('Topic', p, id='events', title='Events', description='Site Events')
            topic = p.events
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

        # Previous events subtopic
        if 'previous' not in topic.objectIds():
            _createObjectByType('Topic', topic, id='previous', title='Past Events',
                                description="Events which have already happened.")
            topic = topic.previous
            topic.setAcquireCriteria(True)
            sort_crit = topic.addCriterion('start','ATSortCriterion')
            sort_crit.setReversed(True)
            date_crit = topic.addCriterion('start','ATFriendlyDateCriteria')
            # Set date reference to now
            date_crit.setValue(0)
            # Only take events in the past
            date_crit.setDateRange('-') # This is irrelevant when the date is now
            date_crit.setOperation('less')

        if 'Members' in existing:
            # configure Members folder (already added by the content import)
            members = getattr(p , 'Members')
            members.setTitle('Members')
            members.setDescription("Container for portal members' home directories")
            members.reindexObject()
            
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
                index_html.ZPythonScript_setTitle('Member Search')

    def performMigrationActions(self, p):
        """
        Perform any necessary migration steps.
        """
        out = []

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
        enableSite(portal, iface=IObjectManagerSite)

        components = PersistentComponents()
        components.__bases__ = (base,)
        portal.setSiteManager(components)
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
         'portal_migration':'Handles migrations to newer Plone versions',
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
        if u'recent' not in left:
            left[u'recent'] = portlets.recent.Assignment(count=5)

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
    if context.readDataFile('plone-site.txt') is None:
        return
    site = context.getSite()
    gen = PloneGenerator()
    gen.enableSite(site)

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

def importFinalSteps(context):
    """
    Final Plone import steps.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('plone-final.txt') is None:
        return
    out = []
    site = context.getSite()
    gen = PloneGenerator()
    gen.addDefaultPortlets(site)
    gen.performMigrationActions(site)
    gen.enableSyndication(site, out)
    gen.assignTitles(site, out)

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
