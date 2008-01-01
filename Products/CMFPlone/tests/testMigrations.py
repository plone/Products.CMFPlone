#
# Tests for migration components
#

from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base
from OFS.SimpleItem import SimpleItem
from Products.Archetypes.interfaces import IArchetypeTool
from Products.Archetypes.interfaces import IReferenceCatalog
from Products.Archetypes.interfaces import IUIDCatalog
from Products.ATContentTypes.interface import IATCTTool
from Products.CMFActionIcons.interfaces import IActionIconsTool
from Products.CMFCalendar.interfaces import ICalendarTool
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.interfaces import IActionCategory
from Products.CMFCore.interfaces import IActionInfo
from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.interfaces import ICachingPolicyManager
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IContentTypeRegistry
from Products.CMFCore.interfaces import IDiscussionTool
from Products.CMFCore.interfaces import IMemberDataTool
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import IMetadataTool
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import IRegistrationTool
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.interfaces import ISkinsTool
from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IUndoTool
from Products.CMFCore.interfaces import IURLTool
from Products.CMFCore.interfaces import IConfigurableWorkflowTool
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFDefault.Portal import CMFSite
from Products.CMFDiffTool.interfaces import IDiffTool
from Products.CMFEditions.interfaces import IArchivistTool
from Products.CMFEditions.interfaces import IPortalModifierTool
from Products.CMFEditions.interfaces import IPurgePolicyTool
from Products.CMFEditions.interfaces.IRepository import IRepositoryTool
from Products.CMFEditions.interfaces import IStorageTool
from Products.CMFFormController.interfaces import IFormControllerTool
from Products.CMFQuickInstallerTool.interfaces import IQuickInstallerTool
from Products.CMFPlacefulWorkflow.global_symbols import placeful_prefs_configlet
from Products.CMFPlone.interfaces import IControlPanel
from Products.CMFPlone.interfaces import IFactoryTool
from Products.CMFPlone.interfaces import IInterfaceTool
from Products.CMFPlone.interfaces import IMigrationTool
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces import IPloneTool
from Products.CMFPlone.interfaces import ITranslationServiceTool
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer
from Products.CMFUid.interfaces import IUniqueIdAnnotationManagement
from Products.CMFUid.interfaces import IUniqueIdGenerator
from Products.CMFUid.interfaces import IUniqueIdHandler
from Products.GenericSetup.interfaces import ISetupTool
from Products.MailHost.interfaces import IMailHost
from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool
from Products.PortalTransforms.interfaces import IPortalTransformsTool
from Products.PloneLanguageTool.interfaces import ILanguageTool
from Products.PlonePAS.interfaces.group import IGroupTool
from Products.PlonePAS.interfaces.group import IGroupDataTool
from Products.ResourceRegistries.interfaces import ICSSRegistry
from Products.ResourceRegistries.interfaces import IJSRegistry
from Products.CMFPlone.migrations.migration_util import loadMigrationProfile

from Products.CMFPlone.migrations.v2_5.final_two51 import fixupPloneLexicon

from Products.CMFPlone.migrations.v2_5.two51_two52 import setLoginFormInCookieAuth
from Products.CMFPlone.migrations.v2_5.two52_two53 import addMissingMimeTypes
from Products.CMFPlone.migrations.v2_5.two53_two54 import addGSSteps
from Products.CMFPlone.migrations.v2_5.two53_two54 import PROF_ID

from Products.CMFPlone.migrations.v3_0.alphas import enableZope3Site
from Products.CMFPlone.migrations.v3_0.alphas import migrateOldActions
from Products.CMFPlone.migrations.v3_0.alphas import updateActionsI18NDomain
from Products.CMFPlone.migrations.v3_0.alphas import updateFTII18NDomain
from Products.CMFPlone.migrations.v3_0.alphas import convertLegacyPortlets
from Products.CMFPlone.migrations.v3_0.alphas import registerToolsAsUtilities
from Products.CMFPlone.migrations.v3_0.alphas import installKss
from Products.CMFPlone.migrations.v3_0.alphas import addReaderAndEditorRoles
from Products.CMFPlone.migrations.v3_0.alphas import migrateLocalroleForm
from Products.CMFPlone.migrations.v3_0.alphas import reorderUserActions
from Products.CMFPlone.migrations.v3_0.alphas import updatePASPlugins
from Products.CMFPlone.migrations.v3_0.alphas import updateKukitJS
from Products.CMFPlone.migrations.v3_0.alphas import addCacheForResourceRegistry
from Products.CMFPlone.migrations.v3_0.alphas import removeTablelessSkin
from Products.CMFPlone.migrations.v3_0.alphas import addObjectProvidesIndex
from Products.CMFPlone.migrations.v3_0.alphas import restorePloneTool
from Products.CMFPlone.migrations.v3_0.alphas import installProduct

from Products.CMFPlone.migrations.v3_0.betas import migrateHistoryTab
from Products.CMFPlone.migrations.v3_0.betas import changeOrderOfActionProviders
from Products.CMFPlone.migrations.v3_0.betas import cleanupOldActions
from Products.CMFPlone.migrations.v3_0.betas import cleanDefaultCharset
from Products.CMFPlone.migrations.v3_0.betas import addAutoGroupToPAS
from Products.CMFPlone.migrations.v3_0.betas import removeS5Actions
from Products.CMFPlone.migrations.v3_0.betas import addCacheForKSSRegistry
from Products.CMFPlone.migrations.v3_0.betas import addContributorToCreationPermissions
from Products.CMFPlone.migrations.v3_0.betas import removeSharingAction
from Products.CMFPlone.migrations.v3_0.betas import addEditorToSecondaryEditorPermissions
from Products.CMFPlone.migrations.v3_0.betas import updateEditActionConditionForLocking
from Products.CMFPlone.migrations.v3_0.betas import addOnFormUnloadJS

from Products.CMFPlone.migrations.v3_0.betas import beta3_rc1
from Products.CMFPlone.migrations.v3_0.betas import moveKupuAndCMFPWControlPanel
from Products.CMFPlone.migrations.v3_0.betas import updateLanguageControlPanel
from Products.CMFPlone.migrations.v3_0.betas import updateTopicTitle
from Products.CMFPlone.migrations.v3_0.betas import cleanupActionProviders
from Products.CMFPlone.migrations.v3_0.betas import hidePropertiesAction

from Products.CMFPlone.migrations.v3_0.rcs import addIntelligentText

from Products.CMFPlone.migrations.v3_0.final_three0x import installNewModifiers

from five.localsitemanager.registry import FiveVerifyingAdapterLookup

from zope.app.cache.interfaces.ram import IRAMCache
from zope.app.component.hooks import clearSite
from zope.app.component.interfaces import ISite
from zope.component import getGlobalSiteManager
from zope.component import getSiteManager
from zope.component import getUtility, getMultiAdapter, queryUtility

from plone.app.i18n.locales.interfaces import IContentLanguages
from plone.app.i18n.locales.interfaces import ICountries
from plone.app.i18n.locales.interfaces import IMetadataLanguages

from plone.app.redirector.interfaces import IRedirectionStorage
from plone.contentrules.engine.interfaces import IRuleStorage

from plone.app.portlets import portlets
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY as CONTEXT_PORTLETS


class BogusMailHost(SimpleItem):
    meta_type = 'Bad Mailer'
    title = 'Mailer'
    smtp_port = 37
    smtp_host = 'my.badhost.com'


class MigrationTest(PloneTestCase.PloneTestCase):

    def removeActionFromTool(self, action_id, category=None, action_provider='portal_actions'):
        # Removes an action from portal_actions
        tool = getattr(self.portal, action_provider)
        if category is None:
            if action_id in tool.objectIds() and IActionInfo.providedBy(tool._getOb(action_id)):
                tool._delOb(action_id)
        else:
            if category in tool.objectIds() and IActionCategory.providedBy(tool._getOb(category)):
                if action_id in tool.objectIds() and IActionInfo.providedBy(tool._getOb(action_id)):
                    tool._delOb(action_id)

    def removeActionIconFromTool(self, action_id, category='plone'):
        # Removes an action icon from portal_actionicons
        tool = getattr(self.portal, 'portal_actionicons')
        try:
            tool.removeActionIcon(category, action_id)
        except KeyError:
            pass # No icon associated

    def addResourceToJSTool(self, resource_name):
        # Registers a resource with the javascripts tool
        tool = getattr(self.portal, 'portal_javascripts')
        if not resource_name in tool.getResourceIds():
            tool.registerScript(resource_name)

    def addResourceToCSSTool(self, resource_name):
        # Registers a resource with the css tool
        tool = getattr(self.portal, 'portal_css')
        if not resource_name in tool.getResourceIds():
            tool.registerStylesheet(resource_name)

    def removeSiteProperty(self, property_id):
        # Removes a site property from portal_properties
        tool = getattr(self.portal, 'portal_properties')
        sheet = getattr(tool, 'site_properties')
        if sheet.hasProperty(property_id):
            sheet.manage_delProperties([property_id])

    def addSiteProperty(self, property_id):
        # adds a site property to portal_properties
        tool = getattr(self.portal, 'portal_properties')
        sheet = getattr(tool, 'site_properties')
        if not sheet.hasProperty(property_id):
            sheet.manage_addProperty(property_id,[],'lines')

    def removeNavTreeProperty(self, property_id):
        # Removes a navtree property from portal_properties
        tool = getattr(self.portal, 'portal_properties')
        sheet = getattr(tool, 'navtree_properties')
        if sheet.hasProperty(property_id):
            sheet.manage_delProperties([property_id])

    def addNavTreeProperty(self, property_id):
        # adds a navtree property to portal_properties
        tool = getattr(self.portal, 'portal_properties')
        sheet = getattr(tool, 'navtree_properties')
        if not sheet.hasProperty(property_id):
            sheet.manage_addProperty(property_id,[],'lines')

    def removeMemberdataProperty(self, property_id):
        # Removes a memberdata property from portal_memberdata
        tool = getattr(self.portal, 'portal_memberdata')
        if tool.hasProperty(property_id):
            tool.manage_delProperties([property_id])

    def uninstallProduct(self, product_name):
        # Removes a product
        tool = getattr(self.portal, 'portal_quickinstaller')
        if tool.isProductInstalled(product_name):
            tool.uninstallProducts([product_name])

    def addSkinLayer(self, layer, skin='Plone Default', pos=None):
        # Adds a skin layer at pos. If pos is None, the layer is appended
        path = self.skins.getSkinPath(skin)
        path = [x.strip() for x in path.split(',')]
        if layer in path:
            path.remove(layer)
        if pos is None:
            path.append(layer)
        else:
            path.insert(pos, layer)
        self.skins.addSkinSelection(skin, ','.join(path))

    def removeSkinLayer(self, layer, skin='Plone Default'):
        # Removes a skin layer from skin
        path = self.skins.getSkinPath(skin)
        path = [x.strip() for x in path.split(',')]
        if layer in path:
            path.remove(layer)
            self.skins.addSkinSelection(skin, ','.join(path))


class TestMigrations_v2_5_0(MigrationTest):

    def afterSetUp(self):
        self.profile = 'profile-Products.CMFPlone.migrations:2.5final-2.5.1'
        self.actions = self.portal.portal_actions
        self.css = self.portal.portal_css

    def testRemovePloneCssFromRR(self):
        # Check to ensure that plone.css gets removed from portal_css
        self.css.registerStylesheet('plone.css', media='all')
        self.failUnless('plone.css' in self.css.getResourceIds())
        loadMigrationProfile(self.portal, self.profile, ('cssregistry', ))
        # plone.css removcal test
        self.failIf('plone.css' in self.css.getResourceIds())

    def testAddEventRegistrationJS(self):
        # Make sure event registration is added
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('event-registration.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('event-registration.js' in script_ids)
        loadMigrationProfile(self.portal, self.profile, ('jsregistry', ))
        # event registration test
        script_ids = jsreg.getResourceIds()
        self.failUnless('event-registration.js' in script_ids)
        self.assertEqual(jsreg.getResourcePosition('event-registration.js'), 0)

    def tesFixObjDeleteAction(self):
        # Prepare delete actions test
        editActions = ('delete',)
        for a in editActions:
            self.removeActionFromTool(a, category='object_buttons')
        loadMigrationProfile(self.portal, self.profile, ('actions', ))
        # delete action tests
        actions = [x.id for x in self.actions.object_buttons.listActions()
                   if x.id in editActions]
        # check that all of our deleted actions are now present
        for a in editActions:
            self.failUnless(a in actions)
        # ensure that they are present only once
        self.failUnlessEqual(len(editActions), len(actions))

    def testFixupPloneLexicon(self):
        # Should update the plone_lexicon pipeline
        lexicon = self.portal.portal_catalog.plone_lexicon
        lexicon._pipeline = (object(), object())
        # Test it twice
        for i in range(2):
            fixupPloneLexicon(self.portal, [])
            self.failUnless(isinstance(lexicon._pipeline[0], Splitter))
            self.failUnless(isinstance(lexicon._pipeline[1], CaseNormalizer))


class TestMigrations_v2_5_1(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.memberdata = self.portal.portal_memberdata
        self.catalog = self.portal.portal_catalog
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.workflow = self.portal.portal_workflow
        self.css = self.portal.portal_css

    def testSetLoginFormInCookieAuth(self):
        setLoginFormInCookieAuth(self.portal, [])
        cookie_auth = self.portal.acl_users.credentials_cookie_auth
        self.failUnlessEqual(cookie_auth.getProperty('login_path'),
                             'require_login')

    def testSetLoginFormNoCookieAuth(self):
        # Shouldn't error
        uf = self.portal.acl_users
        uf._delOb('credentials_cookie_auth')
        setLoginFormInCookieAuth(self.portal, [])

    def testSetLoginFormAlreadyChanged(self):
        # Shouldn't change the value if it's not the default
        cookie_auth = self.portal.acl_users.credentials_cookie_auth
        cookie_auth.manage_changeProperties(login_path='foo')
        out = []
        setLoginFormInCookieAuth(self.portal, out)
        self.failIf(len(out) > 0)
        self.failIfEqual(cookie_auth.getProperty('login_path'),
                         'require_login')

class TestMigrations_v2_5_2(MigrationTest):

    def afterSetUp(self):
        self.mimetypes = self.portal.mimetypes_registry
        
    def testMissingMimeTypes(self):
        # we're testing for 'text/x-web-markdown' and 'text/x-web-textile'
        missing_types = ['text/x-web-markdown', 'text/x-web-textile']
        # since we're running a full 2.5.4 instance in this test, the missing
        # types might in fact already be there:
        current_types = self.mimetypes.list_mimetypes()
        types_to_delete = []
        for mtype in missing_types:
            if mtype in current_types:
                types_to_delete.append(mtype)
        if types_to_delete:
            self.mimetypes.manage_delObjects(types_to_delete)
        # now they're gone:
        self.failIf(set(self.mimetypes.list_mimetypes()).issuperset(set(missing_types)))
        out = []
        addMissingMimeTypes(self.portal, out)
        # now they're back:
        self.failUnless(set(self.mimetypes.list_mimetypes()).issuperset(set(missing_types)))


class TestMigrations_v2_5_4(MigrationTest):

    def afterSetUp(self):
        self.setup = self.portal.portal_setup

    def testAddGSSteps(self):
        # unset the gs profile
        self.setup._baseline_context_id = ''
        self.assertEqual(self.setup.getBaselineContextID(), '')
        addGSSteps(self.portal, [])
        self.assertEqual(self.setup.getBaselineContextID(),
                         'profile-' + PROF_ID)

    def testAddGSStepsAlreadyThere(self):
        # set a bogus existing profile, ensure we don't change it
        self.setup._baseline_context_id = 'profile-Bogus:bogus'
        self.assertEqual(self.setup.getBaselineContextID(),
                         'profile-Bogus:bogus')
        addGSSteps(self.portal, [])
        self.assertEqual(self.setup.getBaselineContextID(),
                         'profile-Bogus:bogus')

    def testAddGSStepsNoPloneStep(self):
        # if the plone step is not there, don't set it
        # first remove it from the registry
        self.setup._baseline_context_id = ''
        from Products.GenericSetup.registry import _profile_registry
        _profile_registry._profile_ids.remove(PROF_ID)
        prof_info = _profile_registry._profile_info[PROF_ID]
        del _profile_registry._profile_info[PROF_ID]

        # Then go through the normal migration process
        self.assertEqual(self.setup.getBaselineContextID(),
                         '')
        addGSSteps(self.portal, [])
        self.assertEqual(self.setup.getBaselineContextID(),
                         '')
        # restore registry, because this is not undone by the transaction
        _profile_registry._profile_ids.append(PROF_ID)
        _profile_registry._profile_info[PROF_ID] = prof_info

    def testAddGSStepsNoTool(self):
        # do nothing if there's no tool
        self.portal._delObject('portal_setup')
        addGSSteps(self.portal, [])


class TestMigrations_v3_0_Actions(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.types = self.portal.portal_types
        self.workflow = self.portal.portal_workflow
        
        # Create dummy old ActionInformation
        self.reply = ActionInformation('reply',
            title='Reply',
            category='reply_actions',
            condition='context/replyAllowed',
            permissions=(AccessInactivePortalContent, ),
            priority=10,
            visible=True,
            action='context/reply'
        )
        self.discussion = self.portal.portal_discussion
        self.discussion._actions = (self.reply, )

    def testMigrateActions(self):
        self.failUnless(self.discussion._actions == (self.reply, ))

        # Test it twice
        for i in range(2):
            migrateOldActions(self.portal, [])
            reply_actions = getattr(self.actions, 'reply_actions', None)
            self.failIf(reply_actions is None)
            reply = getattr(reply_actions, 'reply', None)
            self.failIf(reply is None)
            self.failUnless(isinstance(reply, Action))
            # Verify all data has been migrated correctly to the new Action
            data = reply.getInfoData()[0]
            self.assertEquals(data['category'], 'reply_actions')
            self.assertEquals(data['title'], 'Reply')
            self.assertEquals(data['visible'], True)
            self.assertEquals(data['permissions'], (AccessInactivePortalContent, ))
            self.assertEquals(data['available'].text, 'context/replyAllowed')
            self.assertEquals(data['url'].text, 'context/reply')
            # Make sure the original action has been removed
            self.failUnless(len(self.discussion._actions) == 0)

    def testUpdateActionsI18NDomain(self):
        migrateOldActions(self.portal, [])
        reply = self.actions.reply_actions.reply
        self.assertEquals(reply.i18n_domain, '')        
        # Test it twice
        for i in range(2):
            updateActionsI18NDomain(self.portal, [])
            self.assertEquals(reply.i18n_domain, 'plone')

    def testHistoryActionID(self):
        # Test it twice
        for i in range(2):
            migrateHistoryTab(self.portal, [])
            objects = getattr(self.actions, 'object', None)
            self.failIf('rss' in objects.objectIds())

    def testProviderCleanup(self):
        self.actions.addActionProvider("portal_membership")
        self.failUnless("portal_membership" in self.actions.listActionProviders())
        # Test it twice
        for i in range(2):
            cleanupActionProviders(self.portal, [])
            self.failIf("portal_membership" in self.actions.listActionProviders())

    def testRemovePropertiesActions(self):
        ti = self.types.getTypeInfo("Document")
        if ti.getActionObject("object/properties") is None:
            ti.addAction("metadata", "name", "action", "condition",
                    "permission", "object",)
        # Test it twice
        for i in range(2):
            hidePropertiesAction(self.portal, [])
            self.failUnless(ti.getActionObject("object/metadata") is None)

    def beforeTearDown(self):
        if len(self.discussion._actions) > 0:
            self.discussion._actions = ()


class TestMigrations_v2_5_x(MigrationTest):

    def afterSetUp(self):
        self.profile = 'profile-Products.CMFPlone.migrations:2.5.x-3.0a1'
        self.cp = self.portal.portal_controlpanel
        self.icons = self.portal.portal_actionicons
        self.types = self.portal.portal_types
        self.properties = self.portal.portal_properties

    def disableSite(self, obj, iface=ISite):
        # We need our own disableSite method as the CMF portal implements
        # ISite directly, so we cannot remove it, like the disableSite method
        # in Five.component would have done
        from ZPublisher.BeforeTraverse import unregisterBeforeTraverse
        from Products.Five.component import HOOK_NAME
        obj = aq_base(obj)
        if not iface.providedBy(obj):
            raise TypeError('Object must be a site.')
        unregisterBeforeTraverse(obj, HOOK_NAME)
        if hasattr(obj, HOOK_NAME):
            delattr(obj, HOOK_NAME)

    def testEnableZope3Site(self):
        # First we remove the site and site manager
        self.disableSite(self.portal)
        clearSite(self.portal)
        self.portal.setSiteManager(None)
        gsm = getGlobalSiteManager()
        # Test it twice
        for i in range(2):
            enableZope3Site(self.portal, [])
            # And see if we have an ISite with a local site manager
            self.failUnless(ISite.providedBy(self.portal))
            sm = getSiteManager(self.portal)
            self.failIf(gsm is sm)
            lc = sm.utilities.LookupClass
            self.failUnless(lc == FiveVerifyingAdapterLookup)

        # Test the lookupclass migration
        sm.utilities.LookupClass = None
        # Test it twice
        for i in range(2):
            enableZope3Site(self.portal, [])
            self.failUnless(sm.utilities.LookupClass == FiveVerifyingAdapterLookup)
            self.failUnless(sm.utilities.__parent__ == sm)
            self.failUnless(sm.__parent__ == self.portal)

    def testUpdateFTII18NDomain(self):
        doc = self.types.Document
        doc.i18n_domain = ''
        # Test it twice
        for i in range(2):
            updateFTII18NDomain(self.portal, [])
            self.assertEquals(doc.i18n_domain, 'plone')

    def testAddNewCSSFiles(self):
        cssreg = self.portal.portal_css
        added_ids = ['navtree.css', 'invisibles.css', 'forms.css']
        for id in added_ids:
            cssreg.unregisterResource(id)
        stylesheet_ids = cssreg.getResourceIds()
        for id in added_ids:
            self.failIf(id in stylesheet_ids)
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('cssregistry', ))
            stylesheet_ids = cssreg.getResourceIds()
            for id in added_ids:
                self.failUnless(id in stylesheet_ids)

    def testAddDefaultAndForbiddenContentTypesProperties(self):
        # Should add the forbidden_contenttypes and default_contenttype property
        self.removeSiteProperty('forbidden_contenttypes')
        self.removeSiteProperty('default_contenttype')
        self.failIf(self.properties.site_properties.hasProperty('forbidden_contenttypes'))
        self.failIf(self.properties.site_properties.hasProperty('default_contenttype'))
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('propertiestool', ))
            self.failUnless(self.properties.site_properties.hasProperty('forbidden_contenttypes'))
            self.failUnless(self.properties.site_properties.hasProperty('default_contenttype'))
            self.failUnless(self.properties.site_properties.forbidden_contenttypes ==
                ('text/structured', 'text/restructured', 'text/x-rst',
                'text/plain', 'text/plain-pre', 'text/x-python',
                'text/x-web-markdown', 'text/x-web-intelligent', 'text/x-web-textile')
            )

    def testAddIconForMarkupAndCalendarConfiglet(self):
        self.removeActionIconFromTool('MarkupSettings')
        self.removeActionIconFromTool('CalendarSettings')
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('action-icons', ))
            self.failUnless('MarkupSettings' in [x.getActionId() for x in self.icons.listActionIcons()])
            self.failUnless('CalendarSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddMarkupAndCalendarConfiglet(self):
        self.removeActionFromTool('MarkupSettings', action_provider='portal_controlpanel')
        self.removeActionFromTool('CalendarSettings', action_provider='portal_controlpanel')
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('controlpanel', ))
            self.failUnless('MarkupSettings' in [action.getId() for action in self.cp.listActions()])
            self.failUnless('CalendarSettings' in [x.getId() for x in self.cp.listActions()])
            types = self.cp.getActionObject('Plone/MarkupSettings')
            cal = self.cp.getActionObject('Plone/CalendarSettings')
            self.assertEquals(types.action.text,
                              'string:${portal_url}/@@markup-controlpanel')
            self.assertEquals(cal.title, 'Calendar')
            self.assertEquals(cal.action.text,
                              'string:${portal_url}/@@calendar-controlpanel')

    def testTablelessRemoval(self):
        st = getToolByName(self.portal, "portal_skins")
        if "Plone Tableless" not in st.getSkinSelections():
            st.addSkinSelection('Plone Tableless', 'one,two', make_default=True)
        # Test it twice
        for i in range(2):
            removeTablelessSkin(self.portal, [])
            self.failIf('Plone Tableless' in st.getSkinSelections())
            self.failIf(st.default_skin == 'Plone Tableless')

    def testLegacyPortletsConverted(self):
        self.setRoles(('Manager',))
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=self.portal)
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=self.portal)
        
        left = getMultiAdapter((self.portal, leftColumn,), IPortletAssignmentMapping, context=self.portal)
        right = getMultiAdapter((self.portal, rightColumn,), IPortletAssignmentMapping, context=self.portal)
        
        for k in left:
            del left[k]
        for k in right:
            del right[k]

        self.portal.left_slots = ['here/portlet_recent/macros/portlet',
                                  'here/portlet_news/macros/portlet',
                                  'here/portlet_related/macros/portlet']
        self.portal.right_slots = ['here/portlet_login/macros/portlet',
                                   'here/portlet_languages/macros/portlet']

        # Test it twice
        for i in range(2):
            convertLegacyPortlets(self.portal, [])

            self.assertEquals(self.portal.left_slots, [])
            self.assertEquals(self.portal.right_slots, [])

            lp = left.values()
            self.assertEquals(2, len(lp))

            self.failUnless(isinstance(lp[0], portlets.recent.Assignment))
            self.failUnless(isinstance(lp[1], portlets.news.Assignment))

            rp = right.values()
            self.assertEquals(1, len(rp))
            self.failUnless(isinstance(rp[0], portlets.login.Assignment))

            members = self.portal.Members
            portletAssignments = getMultiAdapter((members, rightColumn,), ILocalPortletAssignmentManager)
            self.assertEquals(True, portletAssignments.getBlacklistStatus(CONTEXT_PORTLETS))

    def testLegacyPortletsConvertedNoSlots(self):
        self.setRoles(('Manager',))
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=self.portal)
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=self.portal)
        
        left = getMultiAdapter((self.portal, leftColumn,), IPortletAssignmentMapping, context=self.portal)
        right = getMultiAdapter((self.portal, rightColumn,), IPortletAssignmentMapping, context=self.portal)
        
        for k in left:
            del left[k]
        for k in right:
            del right[k]
            
        self.portal.left_slots = ['here/portlet_recent/macros/portlet',
                                  'here/portlet_news/macros/portlet']
        if hasattr(self.portal.aq_base, 'right_slots'):
            delattr(self.portal, 'right_slots')
        
        convertLegacyPortlets(self.portal, [])
        
        self.assertEquals(self.portal.left_slots, [])
        
        lp = left.values()
        self.assertEquals(2, len(lp))
        
        self.failUnless(isinstance(lp[0], portlets.recent.Assignment))
        self.failUnless(isinstance(lp[1], portlets.news.Assignment))
        
        rp = right.values()
        self.assertEquals(0, len(rp))
        
        members = self.portal.Members
        portletAssignments = getMultiAdapter((members, rightColumn,), ILocalPortletAssignmentManager)
        self.assertEquals(True, portletAssignments.getBlacklistStatus(CONTEXT_PORTLETS))
        
    def testLegacyPortletsConvertedBadSlots(self):
        self.setRoles(('Manager',))
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=self.portal)
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=self.portal)
        
        left = getMultiAdapter((self.portal, leftColumn,), IPortletAssignmentMapping, context=self.portal)
        right = getMultiAdapter((self.portal, rightColumn,), IPortletAssignmentMapping, context=self.portal)
        
        for k in left:
            del left[k]
        for k in right:
            del right[k]
        
        self.portal.left_slots = ['here/portlet_recent/macros/portlet',
                                  'here/portlet_news/macros/portlet',
                                  'foobar',]
        self.portal.right_slots = ['here/portlet_login/macros/portlet']
        
        convertLegacyPortlets(self.portal, [])
        
        self.assertEquals(self.portal.left_slots, [])
        self.assertEquals(self.portal.right_slots, [])
        
        lp = left.values()
        self.assertEquals(2, len(lp))

        self.failUnless(isinstance(lp[0], portlets.recent.Assignment))
        self.failUnless(isinstance(lp[1], portlets.news.Assignment))
        
        rp = right.values()
        self.assertEquals(1, len(rp))
        self.failUnless(isinstance(rp[0], portlets.login.Assignment))
        
        members = self.portal.Members
        portletAssignments = getMultiAdapter((members, rightColumn,), ILocalPortletAssignmentManager)
        self.assertEquals(True, portletAssignments.getBlacklistStatus(CONTEXT_PORTLETS))
        
    def testLegacyPortletsConvertedNoMembersFolder(self):
        self.setRoles(('Manager',))
        leftColumn = getUtility(IPortletManager, name=u'plone.leftcolumn', context=self.portal)
        rightColumn = getUtility(IPortletManager, name=u'plone.rightcolumn', context=self.portal)
        
        left = getMultiAdapter((self.portal, leftColumn,), IPortletAssignmentMapping, context=self.portal)
        right = getMultiAdapter((self.portal, rightColumn,), IPortletAssignmentMapping, context=self.portal)
        
        for k in left:
            del left[k]
        for k in right:
            del right[k]
        
        self.portal.left_slots = ['here/portlet_recent/macros/portlet',
                                  'here/portlet_news/macros/portlet',
                                  'foobar',]
        self.portal.right_slots = ['here/portlet_login/macros/portlet']
        
        self.portal._delObject('Members')
        
        convertLegacyPortlets(self.portal, [])
        
        self.assertEquals(self.portal.left_slots, [])
        self.assertEquals(self.portal.right_slots, [])
        
        lp = left.values()
        self.assertEquals(2, len(lp))
        
        self.failUnless(isinstance(lp[0], portlets.recent.Assignment))
        self.failUnless(isinstance(lp[1], portlets.news.Assignment))
        
        rp = right.values()
        self.assertEquals(1, len(rp))
        self.failUnless(isinstance(rp[0], portlets.login.Assignment))

    def testRegisterToolsAsUtilities(self):
        sm = getSiteManager(self.portal)
        interfaces = (ISiteRoot, IPloneSiteRoot, IInterfaceTool,
                      IMigrationTool, IActionIconsTool, ISyndicationTool,
                      IMetadataTool, IPropertiesTool, IUndoTool, IMailHost,
                      IUniqueIdAnnotationManagement, IUniqueIdGenerator,
                      IDiffTool, IATCTTool, IMimetypesRegistryTool,
                      IPortalTransformsTool, IDiscussionTool, )
        for i in interfaces:
            sm.unregisterUtility(provided=i)
        registerToolsAsUtilities(self.portal, [])
        for i in interfaces:
            self.failIf(sm.queryUtility(i) is None)

        for i in interfaces:
            sm.unregisterUtility(provided=i)
        registerToolsAsUtilities(self.portal, [])
        registerToolsAsUtilities(self.portal, [])
        for i in interfaces:
            self.failIf(sm.queryUtility(i) is None)

    def testDontRegisterToolsAsUtilities(self):
        sm = getSiteManager(self.portal)
        interfaces = (ILanguageTool, IArchivistTool, IPortalModifierTool,
                      IPurgePolicyTool, IRepositoryTool, IStorageTool,
                      IFormControllerTool, IReferenceCatalog, IUIDCatalog,
                      ICalendarTool, IActionsTool, ICatalogTool,
                      IContentTypeRegistry, ISkinsTool, ITypesTool, IURLTool,
                      IConfigurableWorkflowTool, IPloneTool, ICSSRegistry,
                      IJSRegistry, IUniqueIdHandler, IFactoryTool,
                      IMembershipTool, IGroupTool, IGroupDataTool,
                      IMemberDataTool, IArchetypeTool, ICachingPolicyManager,
                      IRegistrationTool, ITranslationServiceTool,
                      IControlPanel, ISetupTool, IQuickInstallerTool,
                     )
        for i in interfaces:
            sm.unregisterUtility(provided=i)
        registerToolsAsUtilities(self.portal, [])
        for i in interfaces:
            self.failUnless(sm.queryUtility(i) is None)

        for i in interfaces:
            sm.unregisterUtility(provided=i)
        registerToolsAsUtilities(self.portal, [])
        registerToolsAsUtilities(self.portal, [])
        for i in interfaces:
            self.failUnless(sm.queryUtility(i) is None)


class TestMigrations_v3_0_alpha1(MigrationTest):

    def afterSetUp(self):
        self.profile = 'profile-Products.CMFPlone.migrations:3.0a1-3.0a2'
        self.actions = self.portal.portal_actions
        self.cp = self.portal.portal_controlpanel

    def testUpdateSearchAndMailHostConfiglet(self):
        search = self.cp.getActionObject('Plone/SearchSettings')
        mail = self.cp.getActionObject('Plone/MailHost')
        search.action = Expression('string:search')
        mail.action = Expression('string:mail')
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('controlpanel', ))
            search = self.cp.getActionObject('Plone/SearchSettings')
            mail = self.cp.getActionObject('Plone/MailHost')
            self.assertEquals(search.title, 'Search')
            self.assertEquals(search.action.text,
                              'string:${portal_url}/@@search-controlpanel')
            self.assertEquals(mail.title, 'Mail')
            self.assertEquals(mail.action.text,
                              'string:${portal_url}/@@mail-controlpanel')

    def testInstallRedirectorUtility(self):
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IRedirectionStorage)
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('componentregistry', ))
            self.failIf(sm.queryUtility(IRedirectionStorage) is None)

    def testUpdateRtlCSSexpression(self):
        cssreg = self.portal.portal_css
        rtl = cssreg.getResource('RTL.css')
        rtl.setExpression('string:foo')
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('cssregistry', ))
            expr = rtl.getExpression()
            self.failUnless(expr == "python:portal.restrictedTraverse('@@plone_portal_state').is_rtl()")

    def testAddReaderEditorRoles(self):
        self.portal._delRoles(['Reader', 'Editor'])
        # Test it twice
        for i in range(2):
            addReaderAndEditorRoles(self.portal, [])
            self.failUnless('Reader' in self.portal.valid_roles())
            self.failUnless('Editor' in self.portal.valid_roles())
            self.failUnless('Reader' in self.portal.acl_users.portal_role_manager.listRoleIds())
            self.failUnless('Editor' in self.portal.acl_users.portal_role_manager.listRoleIds())
            self.failUnless('View' in [r['name'] for r in self.portal.permissionsOfRole('Reader') if r['selected']])
            self.failUnless('Modify portal content' in [r['name'] for r in self.portal.permissionsOfRole('Editor') if r['selected']])

    def testAddReaderEditorRolesPermissionOnly(self):
        self.portal.manage_permission('View', [], True)
        self.portal.manage_permission('Modify portal content', [], True)
        # Test it twice
        for i in range(2):
            addReaderAndEditorRoles(self.portal, [])
            self.failUnless('Reader' in self.portal.valid_roles())
            self.failUnless('Editor' in self.portal.valid_roles())
            self.failUnless('Reader' in self.portal.acl_users.portal_role_manager.listRoleIds())
            self.failUnless('Editor' in self.portal.acl_users.portal_role_manager.listRoleIds())
            self.failUnless('View' in [r['name'] for r in self.portal.permissionsOfRole('Reader') if r['selected']])
            self.failUnless('Modify portal content' in [r['name'] for r in self.portal.permissionsOfRole('Editor') if r['selected']])

    def testMigrateLocalroleForm(self):
        fti = self.portal.portal_types['Document']
        aliases = fti.getMethodAliases()
        aliases['sharing'] = 'folder_localrole_form'
        fti.setMethodAliases(aliases)
        fti.addAction('test', 'Test', 'string:${object_url}/folder_localrole_form', None, 'View', 'object')
        # Test it twice
        for i in range(2):
            migrateLocalroleForm(self.portal, [])
            self.assertEquals('@@sharing', fti.getMethodAliases()['sharing'])
            test_action = fti.listActions()[-1]
            self.assertEquals('string:${object_url}/@@sharing', test_action.getActionExpression())

    def testReorderUserActions(self):
        self.actions.user.moveObjectsToTop(['logout', 'undo', 'join'])
        # Test it twice
        for i in range(2):
            reorderUserActions(self.portal, [])
            # build a dict that has the position as the value to make it easier
            # to compare postions in the ordered list of actions
            n = 0
            sort = {}
            for action in self.actions.user.objectIds():
                sort[action] = n
                n += 1
            self.failUnless(sort['mystuff'] < sort['preferences'])
            self.failUnless(sort['preferences'] < sort['undo'])
            self.failUnless(sort['undo'] < sort['logout'])
            self.failUnless(sort['login'] < sort['join'])

    def testReorderUserActionsIncompleteActions(self):
        self.actions.user.moveObjectsToTop(['logout', 'undo', 'join'])
        self.actions.user._delObject('preferences')
        # Test it twice
        for i in range(2):
            reorderUserActions(self.portal, [])
            n = 0
            sort = {}
            for action in self.actions.user.objectIds():
                sort[action] = n
                n += 1
            self.failUnless(sort['mystuff'] < sort['undo'])
            self.failUnless(sort['undo'] < sort['logout'])
            self.failUnless(sort['login'] < sort['join'])

    def testInstallKss(self):
        'Test kss migration'
        jstool = self.portal.portal_javascripts
        csstool = self.portal.portal_css
        mt = self.portal.mimetypes_registry
        mtid = 'text/kss'
        st = self.portal.portal_skins
        skins = ['Plone Default']
        # unregister first
        for id, _compression, _enabled in installKss.js_all:
            jstool.unregisterResource(id)
        for id in installKss.css_all + installKss.kss_all:
            csstool.unregisterResource(id)
        mt.manage_delObjects((mtid, ))
        js_ids = jstool.getResourceIds()
        for id, _compression, _enabled in installKss.js_all:
            self.failIf(id in js_ids)
        css_ids = csstool.getResourceIds()
        for id in installKss.css_all + installKss.kss_all:
            self.failIf(id in css_ids)
        self.failIf(mtid in mt.list_mimetypes())
        selections = st._getSelections()
        for s in skins:
            if not selections.has_key(s):
                continue
            path = st.getSkinPath(s)
            path = [p.strip() for p in  path.split(',')]
            path_changed = False
            if 'plone.kss' in path:
                path.remove('plone.kss')
                path_changed = True
            if 'at.kss' in path:
                path.remove('at.kss')
                path_changed = True
            if path_changed:
                st.addSkinSelection(s, ','.join(path))
        # TODO we cannot remove the directory views, so...
        # Test it twice
        for i in range(2):
            installKss(self.portal, [])
            js_ids = jstool.getResourceIds()
            css_dict = csstool.getResourcesDict()
            for id in installKss.js_unregister:
                self.failIf(id in js_ids)
            for id, _compression, _enabled in installKss.js_all:
                self.assert_(id in js_ids, '%r is not registered' % id)
            for id in installKss.css_all:
                self.assert_(id in css_dict)
            for id in installKss.kss_all:
                self.assert_(id in css_dict)
                value = css_dict[id]
                self.assertEqual(value.getEnabled(), True)
                self.assertEqual(value.getRel(), 'k-stylesheet')
                self.assertEqual(value.getRendering(), 'link')
            self.assert_(mtid in mt.list_mimetypes())
            # check the skins
            selections = st._getSelections()
            for s in skins:
                if not selections.has_key(s):
                   continue
                path = st.getSkinPath(s)
                path = [p.strip() for p in  path.split(',')]
                self.assert_('plone_kss' in path)
                self.assert_('archetypes_kss' in path)
            self.assert_(hasattr(aq_base(st), 'plone_kss'))
            self.assert_(hasattr(aq_base(st), 'archetypes_kss'))


class TestMigrations_v3_0_alpha2(MigrationTest):

    def afterSetUp(self):
        self.profile = 'profile-Products.CMFPlone.migrations:3.0a2-3.0b1'
        self.actions = self.portal.portal_actions
        self.cp = self.portal.portal_controlpanel
        self.icons = self.portal.portal_actionicons
        self.properties = self.portal.portal_properties

    def testAddVariousProperties(self):
        PROPERTIES = ('enable_link_integrity_checks', 'enable_sitemap',
                      'external_links_open_new_window', 'many_groups',
                      'number_of_days_to_keep', 'webstats_js')
        for prop in PROPERTIES:
            self.removeSiteProperty(prop)
        sheet = self.properties.site_properties
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('propertiestool', ))
            for prop in PROPERTIES:
                self.failUnless(sheet.hasProperty(prop))

    def testAddVariousJavaScripts(self):
        jsreg = self.portal.portal_javascripts
        jsreg.registerScript("folder_contents_hideAddItems.js")
        self.failUnless('folder_contents_hideAddItems.js' in jsreg.getResourceIds())
        RESOURCES = ('form_tabbing.js', 'input-label.js', 'toc.js',
                     'webstats.js')
        for r in RESOURCES:
            jsreg.unregisterResource(r)
        script_ids = jsreg.getResourceIds()
        for r in RESOURCES:
            self.failIf(r in script_ids)
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('jsregistry', ))
            script_ids = jsreg.getResourceIds()
            # Removed script
            self.failIf('folder_contents_hideAddItems.js' in script_ids)
            for r in RESOURCES:
                self.failUnless(r in script_ids)
            # form_tabbing tests
            if 'collapsiblesections.js' in script_ids:
                posSE = jsreg.getResourcePosition('form_tabbing.js')
                posHST = jsreg.getResourcePosition('collapsiblesections.js')
                self.failUnless((posSE - 1) == posHST)
            # webstats tests
            if 'webstats.js' in script_ids:
                pos1 = jsreg.getResourcePosition('toc.js')
                pos2 = jsreg.getResourcePosition('webstats.js')
                self.failUnless((pos2 - 1) == pos1)
            # check if enabled
            res = jsreg.getResource('webstats.js')
            self.assertEqual(res.getEnabled(), True)

    def testUpdateKukitJS(self):
        jsreg = self.portal.portal_javascripts
        # put into old state first
        jsreg.unregisterResource('++resource++kukit.js')
        jsreg.unregisterResource('++resource++kukit-devel.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('++resource++kukit.js' in script_ids)
        self.failIf('++resource++kukit-devel.js' in script_ids)
        self.failIf('++resource++kukit-src.js' in script_ids)
        jsreg.registerScript('++resource++kukit.js', compression="none")
        script_ids = jsreg.getResourceIds()
        self.failUnless('++resource++kukit.js' in script_ids)
        # migrate and test again
        updateKukitJS(self.portal, [])
        script_ids = jsreg.getResourceIds()
        self.failUnless('++resource++kukit-src.js' in script_ids)
        resource = jsreg.getResource('++resource++kukit-src.js')
        self.failUnless(resource.getCompression() == 'full')
        # Run the last migration and check that everything is in its
        # place. We must have both the devel and production resources.
        # They both should be uncompressed since kss compresses them
        # directly. Also they should have conditions that switches them.
        beta3_rc1(self.portal)
        script_ids = jsreg.getResourceIds()
        self.failIf('++resource++kukit-src.js' in script_ids)
        resource1 = jsreg.getResource('++resource++kukit.js')
        resource2 = jsreg.getResource('++resource++kukit-devel.js')
        self.failUnless(resource1.getCompression() == 'none')
        self.failUnless(resource2.getCompression() == 'none')
        self.failUnless('@@kss_devel_mode' in resource1.getExpression())
        self.failUnless('@@kss_devel_mode' in resource2.getExpression())
        self.failUnless('isoff' in resource1.getExpression())
        self.failUnless('ison' in resource2.getExpression())

    def testVariousConfiglets(self):
        skins = self.cp.getActionObject('Plone/PortalSkin')
        site = self.cp.getActionObject('Plone/PloneReconfig')
        skins.action = Expression('string:skins')
        site.action = Expression('string:site')
        RENAMED_CONFIGLETS = [
            ('Plone/portal_atct', 'Collection'),
            ('Plone/PloneLanguageTool', 'Language'),
            ('Plone/NavigationSettings', 'Navigation'),
            ('Plone/UsersGroups', 'Users and Groups'),
            ('Plone/UsersGroups2', 'Users and Groups')]
        for ren in RENAMED_CONFIGLETS:
            conf = self.cp.getActionObject(ren[0])
            conf.title = 'wrongtitle'
        ADDED_CONFIGLETS = ('ContentRules', 'HtmlFilter', 'Maintenance',
                            'SecuritySettings', 'TypesSettings')
        for add in ADDED_CONFIGLETS:
            self.removeActionFromTool(add, action_provider='portal_controlpanel')
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('controlpanel', ))
            skins = self.cp.getActionObject('Plone/PortalSkin')
            site = self.cp.getActionObject('Plone/PloneReconfig')
            self.assertEquals(skins.title, 'Themes')
            self.assertEquals(skins.action.text,
                              'string:${portal_url}/@@skins-controlpanel')
            self.assertEquals(site.title, 'Site')
            self.assertEquals(site.action.text,
                              'string:${portal_url}/@@site-controlpanel')
            for ren in RENAMED_CONFIGLETS:
                conf = self.cp.getActionObject(ren[0])
                self.assertEquals(conf.title, ren[1])
            actionids = [x.getId() for x in self.cp.listActions()]
            for add in ADDED_CONFIGLETS:
                self.failUnless(add in actionids)
            htmlfilter = self.cp.getActionObject('Plone/HtmlFilter')
            self.assertEquals(htmlfilter.title, 'HTML Filtering')
            self.assertEquals(htmlfilter.action.text,
                              'string:${portal_url}/@@filter-controlpanel')
            main = self.cp.getActionObject('Plone/Maintenance')
            self.assertEquals(main.title, 'Maintenance')
            self.assertEquals(main.action.text,
                              'string:${portal_url}/@@maintenance-controlpanel')
            security = self.cp.getActionObject('Plone/SecuritySettings')
            self.assertEquals(security.title, 'Security')
            self.assertEquals(security.action.text,
                              'string:${portal_url}/@@security-controlpanel')
            types = self.cp.getActionObject('Plone/TypesSettings')
            self.assertEquals(types.action.text,
                              'string:${portal_url}/@@types-controlpanel')

    def testaddIconsForVariousConfiglets(self):
        ICONS = ('ContentRules', 'HtmlFilter', 'Maintenance',
                 'SecuritySettings', 'TypesSettings')
        for i in ICONS:
            self.removeActionIconFromTool(i)
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('action-icons', ))
            iconids = [x.getActionId() for x in self.icons.listActionIcons()]
            for i in ICONS:
                self.failUnless(i in iconids)

    def testInstallContentrulesAndLanguageUtilities(self):
        sm = getSiteManager()
        INTERFACES = (IRuleStorage, ICountries, IContentLanguages,
                      IMetadataLanguages)
        for i in INTERFACES:
            sm.unregisterUtility(provided=i)
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('componentregistry', ))
            for i in INTERFACES:
                self.failIf(sm.queryUtility(i) is None)

    def testAddEmailCharsetProperty(self):
        if self.portal.hasProperty('email_charset'):
            self.portal.manage_delProperties(['email_charset'])
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('properties', ))
            self.failUnless(self.portal.hasProperty('email_charset'))
            self.assertEquals(self.portal.getProperty('email_charset'), 'utf-8')

    def testUpdateMemberSecurity(self):
        pprop = getToolByName(self.portal, 'portal_properties')
        self.assertEquals(
                pprop.site_properties.getProperty('allowAnonymousViewAbout'),
                False)

        pmembership = getToolByName(self.portal, 'portal_membership')
        self.assertEquals(pmembership.memberareaCreationFlag, False)
        self.assertEquals(self.portal.getProperty('validate_email'), True)

        app_roles = self.portal.rolesOfPermission(permission='Add portal member')
        app_perms = self.portal.permission_settings(permission='Add portal member')
        acquire_check = app_perms[0]['acquire']
        reg_roles = []
        for appperm in app_roles:
            if appperm['selected'] == 'SELECTED':
                reg_roles.append(appperm['name'])
        self.failUnless('Manager' in reg_roles)
        self.failUnless('Owner' in reg_roles)
        self.failUnless(acquire_check == '')

    def testPASPluginInterfaces(self):
        pas = self.portal.acl_users
        from Products.PluggableAuthService.interfaces.plugins import IUserEnumerationPlugin
        pas.plugins.deactivatePlugin(IUserEnumerationPlugin, 'mutable_properties')
        updatePASPlugins(self.portal, [])

        plugin = pas.mutable_properties
        for intf_id in plugin.listInterfaces():
            try:
                intf = pas.plugins._getInterfaceFromName(intf_id)
                self.failUnless('mutable_properties' in pas.plugins.listPluginIds(intf))
            except KeyError:
                # Ignore unregistered interface types 
                pass

    def testAddCacheForResourceRegistry(self):
        ram_cache_id = 'ResourceRegistryCache'
        # first remove the cache manager and make sure it's removed
        self.portal._delObject(ram_cache_id)
        self.failIf(ram_cache_id in self.portal.objectIds())
        cssreg = self.portal.portal_css
        cssreg.ZCacheable_setEnabled(0)
        cssreg.ZCacheable_setManagerId(None)
        self.failIf(cssreg.ZCacheable_enabled())
        self.failUnless(cssreg.ZCacheable_getManagerId() is None)
        jsreg = self.portal.portal_javascripts
        jsreg.ZCacheable_setEnabled(0)
        jsreg.ZCacheable_setManagerId(None)
        self.failIf(jsreg.ZCacheable_enabled())
        self.failUnless(jsreg.ZCacheable_getManagerId() is None)
        # Test it twice
        for i in range(2):
            addCacheForResourceRegistry(self.portal, [])
            self.failUnless(ram_cache_id in self.portal.objectIds())
            self.failUnless(cssreg.ZCacheable_enabled())
            self.failIf(cssreg.ZCacheable_getManagerId() is None)
            self.failUnless(jsreg.ZCacheable_enabled())
            self.failIf(jsreg.ZCacheable_getManagerId() is None)

    def testObjectProvidesIndex(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        if 'object_provides' in catalog.indexes():
            catalog.delIndex('object_provides')
        self.failIf('object_provides' in catalog.indexes())
        # Test it twice
        for i in range(2):
            addObjectProvidesIndex(self.portal, [])
            self.failUnless('object_provides' in catalog.indexes())

    def testMigratePloneTool(self):
        from Products.CMFPlone import ToolNames
        tool = self.portal.plone_utils
        tool.meta_type = 'PlonePAS Utilities Tool'
        # Test it twice
        for i in range(2):
            restorePloneTool(self.portal, [])
            tool = self.portal.plone_utils
            self.assertEquals(ToolNames.UtilsTool, tool.meta_type)

    def testInstallPloneLanguageTool(self):
        CMFSite.manage_delObjects(self.portal, ['portal_languages'])
        self.uninstallProduct('PloneLanguageTool')
        qi = getToolByName(self.portal, "portal_quickinstaller")
        # Test it twice
        for i in range(2):
            installProduct('PloneLanguageTool', self.portal, [])
            self.failUnless(qi.isProductInstalled('PloneLanguageTool'))
            self.failUnless('portal_languages' in self.portal.keys())


class TestMigrations_v3_0(MigrationTest):

    def afterSetUp(self):
        self.profile = 'profile-Products.CMFPlone.migrations:3.0b1-3.0b2'
        self.actions = self.portal.portal_actions
        self.cp = self.portal.portal_controlpanel
        self.icons = self.portal.portal_actionicons
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.workflow = self.portal.portal_workflow
        self.properties = self.portal.portal_properties

    def testAddContentRulesAction(self):
        self.portal.portal_actions.object._delObject('contentrules')
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal, self.profile, ('actions', ))
            self.failUnless('contentrules' in self.portal.portal_actions.object.objectIds())

    def testAddNewBeta2CSSFiles(self):
        cssreg = self.portal.portal_css
        added_ids = ['controlpanel.css']
        for id in added_ids:
            cssreg.unregisterResource(id)
        stylesheet_ids = cssreg.getResourceIds()
        for id in added_ids:
            self.failIf('controlpanel.css' in stylesheet_ids)
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal,
                    'profile-Products.CMFPlone.migrations:3.0b1-3.0b2',
                    steps=["cssregistry"])
            stylesheet_ids = cssreg.getResourceIds()
            for id in added_ids:
                self.failUnless(id in stylesheet_ids)

    def testChangeOrderOfActionProviders(self):
        out = []
        self.actions.deleteActionProvider('portal_types')
        self.actions.addActionProvider('portal_types')
        self.assertEquals(
            self.actions.listActionProviders(),
            ('portal_workflow', 'portal_actions', 'portal_types'))
        # Test it twice
        for i in range(2):
            changeOrderOfActionProviders(self.portal, out)
            self.assertEquals(
                self.actions.listActionProviders(),
                ('portal_workflow', 'portal_types', 'portal_actions'))

    def testCleanupOldActions(self):
        out = []
        reply = Action('reply', title='Reply')
        logged_in = Action('logged_in', title='Logged in')
        change_ownership = Action('change_ownership', title='Change ownership')

        object_ = self.actions.object
        object_tabs = getattr(self.actions, 'object_tabs', None)
        if object_tabs is None:
            category = 'object_tabs'
            self.actions._setObject(category, ActionCategory(id=category))
            object_tabs = self.actions.object_tabs
        if getattr(self.actions, 'global', None) is None:
            category = 'global'
            self.actions._setObject(category, ActionCategory(id=category))

        if not 'reply' in object_.keys():
            object_._setObject('reply', reply)
        user = self.actions.user
        if not 'logged_in' in user.keys():
            user._setObject('logged_in', logged_in)
        if not 'change_ownership' in object_tabs.keys():
            object_tabs._setObject('change_ownership', change_ownership)
        del object_tabs

        # Test it twice
        for i in range(2):
            cleanupOldActions(self.portal, out)
            self.failIf('reply' in object_.keys())
            self.failIf('logged_in' in user.keys())
            self.failIf('object_tabs' in self.actions.keys())
            self.failIf('global' in self.actions.keys())

    def testCharsetCleanup(self):
        if not self.portal.hasProperty('default_charset'):
            self.portal.manage_addProperty('default_charset', '', 'string')
        # Test it twice
        for i in range(2):
            self.portal.manage_changeProperties(default_charset = 'latin1')
            cleanDefaultCharset(self.portal, [])
            self.assertEqual(self.portal.getProperty('default_charset', 'nothere'),
                    'latin1')
        # Test it twice
        for i in range(2):
            self.portal.manage_changeProperties(default_charset = '')
            cleanDefaultCharset(self.portal, [])
            self.assertEqual(self.portal.getProperty('default_charset', 'nothere'),
                    'nothere')

    def testAutoGroupCreated(self):
        pas = self.portal.acl_users
        ids = pas.objectIds(['Automatic Group Plugin'])
        if ids:
            pas.manage_delObjects(ids)
        addAutoGroupToPAS(self.portal, [])
        self.assertEqual(pas.objectIds(['Automatic Group Plugin']),
                ['auto_group'])
        plugin = pas.auto_group
        interfaces = [info['interface'] for info in pas.plugins.listPluginTypeInfo()]
        for iface in interfaces:
            if plugin.testImplements(iface):
                self.failIf('auto_group' not in pas.plugins.listPluginIds(iface))
        self.assertEqual(len(pas.searchGroups(id='AuthenticatedUsers',
                                              exact_match=True)), 1)

    def testPloneS5(self):
        pt = getToolByName(self.portal, "portal_types")
        ait = getToolByName(self.portal, "portal_actionicons")
        document = pt.restrictedTraverse('Document')
        document.addAction('s5_presentation',
            name='View as presentation',
            action="string:${object/absolute_url}/document_s5_presentation",
            condition='python:object.document_s5_alter(test=True)',
            permission='View',
            category='document_actions',
            visible=1,
            )
        ait.addActionIcon(
            category='plone',
            action_id='s5_presentation',
            icon_expr='fullscreenexpand_icon.gif',
            title='View as presentation',
            )
        action_ids = [x.getId() for x in document.listActions()]
        self.failUnless("s5_presentation" in action_ids)
        icon_ids = [x.getActionId() for x in ait.listActionIcons()]
        self.failUnless("s5_presentation" in icon_ids)
        # Test it twice
        for i in range(2):
            removeS5Actions(self.portal, [])
            action_ids = [x.getId() for x in document.listActions()]
            self.failIf("s5_presentation" in action_ids)
            icon_ids = [x.getActionId() for x in ait.listActionIcons()]
            self.failIf("s5_presentation" in icon_ids)

    def testAddCacheForKSSRegistry(self):
        ram_cache_id = 'ResourceRegistryCache'
        kssreg = self.portal.portal_kss
        kssreg.ZCacheable_setEnabled(0)
        kssreg.ZCacheable_setManagerId(None)
        self.failIf(kssreg.ZCacheable_enabled())
        self.failUnless(kssreg.ZCacheable_getManagerId() is None)
        # Test it twice
        for i in range(2):
            addCacheForKSSRegistry(self.portal, [])
            self.failUnless(kssreg.ZCacheable_enabled())
            self.failIf(kssreg.ZCacheable_getManagerId() is None)

    def testAddContributorToCreationPermissions(self):
        self.portal._delRoles(['Contributor',])
        for p in ['Add portal content', 'Add portal folders', 'ATContentTypes: Add Document',
                    'ATContentTypes: Add Event', 'ATContentTypes: Add Favorite',
                    'ATContentTypes: Add File', 'ATContentTypes: Add Folder', 
                    'ATContentTypes: Add Image', 'ATContentTypes: Add Large Plone Folder',
                    'ATContentTypes: Add Link', 'ATContentTypes: Add News Item', ]:
            self.portal.manage_permission(p, ['Manager', 'Owner'], True)
        # Test it twice
        for i in range(2):
            addContributorToCreationPermissions(self.portal, [])
            self.failUnless('Contributor' in self.portal.valid_roles())
            self.failUnless('Contributor' in self.portal.acl_users.portal_role_manager.listRoleIds())
            for p in ['Add portal content', 'Add portal folders', 'ATContentTypes: Add Document',
                        'ATContentTypes: Add Event', 'ATContentTypes: Add Favorite',
                        'ATContentTypes: Add File', 'ATContentTypes: Add Folder', 
                        'ATContentTypes: Add Image', 'ATContentTypes: Add Large Plone Folder',
                        'ATContentTypes: Add Link', 'ATContentTypes: Add News Item', ]:
                self.failUnless(p in [r['name'] for r in 
                                    self.portal.permissionsOfRole('Contributor') if r['selected']])

    def testAddEditorToCreationPermissionsNoStomp(self):
        self.portal.manage_permission('Add portal content', ['Manager'], False)
        # Test it twice
        for i in range(2):
            addContributorToCreationPermissions(self.portal, [])
            roles = sorted([r['name'] for r in self.portal.rolesOfPermission('Add portal content') if r['selected']])
            self.assertEquals(['Contributor', 'Manager'], roles)
            self.assertEquals(False, bool(self.portal.acquiredRolesAreUsedBy('Add portal content')))

    def testAddBeta2VersioningPermissionsToNewRoles(self):
        # This migration just uses GS to apply the role changes,
        # these permissions will not have been installed previously,
        # so this should be safe
        for p in ['CMFEditions: Apply version control',
                  'CMFEditions: Save new version',
                  'CMFEditions: Access previous versions',
                  'CMFEditions: Revert to previous versions',
                  'CMFEditions: Checkout to location']:
            self.portal.manage_permission(p, ['Manager', 'Owner'], True)
        # Test it twice
        for i in range(2):
            loadMigrationProfile(self.portal,
                    'profile-Products.CMFPlone.migrations:3.0b1-3.0b2',
                    steps=["rolemap"])
            for p in ['CMFEditions: Apply version control',
                      'CMFEditions: Save new version',
                      'CMFEditions: Access previous versions']:
                self.failUnless(p in [r['name'] for r in 
                                    self.portal.permissionsOfRole('Contributor') if r['selected']])
                self.failUnless(p in [r['name'] for r in 
                                    self.portal.permissionsOfRole('Editor') if r['selected']])
            for p in ['CMFEditions: Revert to previous versions',
                      'CMFEditions: Checkout to location']:
                self.failUnless(p in [r['name'] for r in 
                                    self.portal.permissionsOfRole('Editor') if r['selected']])

    def testRemoveSharingAction(self):
        fti = self.types['Document']
        fti.addAction(id='local_roles', name='Sharing', 
                      action='string:${object_url}/sharing',
                      condition=None, permission='Manage properties',
                      category='object')
        # Test it twice
        for i in range(2):
            removeSharingAction(self.portal, [])
            self.failIf('local_roles' in [a.id for a in fti.listActions()])

    def testAddContributorToCreationPermissions(self):
        for p in ['Manage properties', 'Modify view template', 'Request review']:
            self.portal.manage_permission(p, ['Manager', 'Owner'], True)
        # Test it twice
        for i in range(2):
            addEditorToSecondaryEditorPermissions(self.portal, [])
            for p in ['Manage properties', 'Modify view template', 'Request review']:
                self.failUnless(p in [r['name'] for r in 
                    self.portal.permissionsOfRole('Editor') if r['selected']])

    def testAddEditorToCreationPermissionsNoStomp(self):
        self.portal.manage_permission('Manage properties', ['Manager'], False)
        # Test it twice
        for i in range(2):
            addEditorToSecondaryEditorPermissions(self.portal, [])
            roles = sorted([r['name'] for r in self.portal.rolesOfPermission('Manage properties') if r['selected']])
            self.assertEquals(['Editor', 'Manager'], roles)
            self.assertEquals(False, bool(self.portal.acquiredRolesAreUsedBy('Manage properties')))

    def testUpdateEditActionConditionForLocking(self):
        out = []
        lockable_types = ['Document', 'Event', 'Favorite', 'File', 'Folder',
                          'Image', 'Large Plone Folder', 'Link',
                          'News Item', 'Topic']
        for contentType in lockable_types:
            fti = self.types.getTypeInfo(contentType)
            for action in fti.listActions():
                if action.getId() == 'edit':
                    action.condition = ''
        # Test it twice
        for i in range(2):
            updateEditActionConditionForLocking(self.portal, out)
            for contentType in lockable_types:
                fti = self.types.getTypeInfo(contentType)
                for action in fti.listActions():
                    if action.getId() == 'edit':
                        expressionCondition = action.condition
                        self.assertEquals(action.condition.text, "not:object/@@plone_lock_info/is_locked_for_current_user|python:True")

    def testUpdateEditExistingActionConditionForLocking(self):
        out = []
        fti = self.types.getTypeInfo('Document')
        for action in fti.listActions():
            if action.getId() == 'edit':
                action.condition = Expression("foo")
        # Test it twice
        for i in range(2):
            updateEditActionConditionForLocking(self.portal, out)
            fti = self.types.getTypeInfo('Document')
            for action in fti.listActions():
                if action.getId() == 'edit':
                    self.assertEquals(action.condition.text, 'foo')

    def testAddOnFormUnloadRegistrationJS(self):
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('unlockOnFormUnload.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('unlockOnFormUnload.js' in script_ids)
        # Test it twice
        for i in range(2):
            addOnFormUnloadJS(self.portal, [])
            script_ids = jsreg.getResourceIds()
            self.failUnless('unlockOnFormUnload.js' in script_ids)

    def testAddRAMCache(self):
        sm = getSiteManager()
        sm.unregisterUtility(provided=IRAMCache)
        util = queryUtility(IRAMCache)
        self.failUnless(util.maxAge == 86400)
        beta3_rc1(self.portal)
        util = queryUtility(IRAMCache)
        self.failUnless(util.maxAge == 3600)

    def testMoveKupuAndCMFPWControlPanel(self):
        kupu = self.cp.getActionObject('Plone/kupu')
        kupu.category = 'Products'
        cmfpw = self.cp.getActionObject('Products/placefulworkflow')
        if cmfpw is None:
            self.cp.registerConfiglet(**placeful_prefs_configlet)
        cmfpw = self.cp.getActionObject('Products/placefulworkflow')
        cmfpw.category = 'Plone'
        # Test it twice
        for i in range(2):
            moveKupuAndCMFPWControlPanel(self.portal, [])
            kupu = self.cp.getActionObject('Plone/kupu')
            self.assertEquals(kupu.getCategory(), 'Plone')
            cmfpw = self.cp.getActionObject('Products/placefulworkflow')
            self.assertEquals(cmfpw.getCategory(), 'Products')

    def testUpdateLanguageControlPanel(self):
        lang = self.cp.getActionObject('Plone/PloneLanguageTool')
        lang.action = Expression('string:lang')
        # Test it twice
        for i in range(2):
            updateLanguageControlPanel(self.portal, [])
            self.assertEquals(lang.action.text,
                              'string:${portal_url}/@@language-controlpanel')

    def testUpdateTopicTitle(self):
        topic = self.types.get('Topic')
        topic.title = 'Unmigrated'
        # Test it twice
        for i in range(2):
            updateTopicTitle(self.portal, [])
            self.failUnless(topic.title == 'Collection')

    def testAddIntelligentText(self):
        # Before migration, the mime type and transforms of intelligent text
        # are not available. They *are* here in a fresh site, so we may need
        # to remove them first for testing. First we remove the transforms,
        # as they depend on the mimetype being there.
        missing_transforms = ["web_intelligent_plain_text_to_html",
                              "html_to_web_intelligent_plain_text"]
        ptr = self.portal.portal_transforms
        current_transforms = ptr.objectIds()
        for trans in missing_transforms:
            if trans in current_transforms:
                ptr.unregisterTransform(trans)
        # Then we remove the mime type
        mime_type = 'text/x-web-intelligent'
        mtr = self.portal.mimetypes_registry
        current_types = mtr.list_mimetypes()
        if mime_type in current_types:
            mtr.manage_delObjects((mime_type,))
        # now all are gone:
        self.failIf(mime_type in mtr.list_mimetypes())
        self.failIf(set(ptr.objectIds()).issuperset(set(missing_transforms)))
        # Test it twice
        for i in range(2):
            addIntelligentText(self.portal, [])
            # now all are back:
            self.failUnless(mime_type in mtr.list_mimetypes())
            self.failUnless(set(ptr.objectIds()).issuperset(set(missing_transforms)))

    def testInstallNewModifiers(self):
        # ensure the new modifiers are installed
        modifiers = self.portal.portal_modifier
        self.failUnless('AbortVersioningOfLargeFilesAndImages' in
                                                          modifiers.objectIds())
        modifiers.manage_delObjects(['AbortVersioningOfLargeFilesAndImages',
                                     'SkipVersioningOfLargeFilesAndImages'])
        self.failIf('AbortVersioningOfLargeFilesAndImages' in
                                                          modifiers.objectIds())
        installNewModifiers(self.portal, [])
        self.failUnless('AbortVersioningOfLargeFilesAndImages' in
                                                          modifiers.objectIds())
        self.failUnless('SkipVersioningOfLargeFilesAndImages' in
                                                          modifiers.objectIds())

    def testInstallNewModifiersTwice(self):
        # ensure that we get no errors when run twice
        modifiers = self.portal.portal_modifier
        installNewModifiers(self.portal, [])
        installNewModifiers(self.portal, [])

    def testInstallNewModifiersDoesNotStompChanges(self):
        # ensure that reinstalling doesn't kill customizations
        modifiers = self.portal.portal_modifier
        modifiers.AbortVersioningOfLargeFilesAndImages.max_size = 1000
        installNewModifiers(self.portal, [])
        self.assertEqual(modifiers.AbortVersioningOfLargeFilesAndImages.max_size,
                         1000)

    def testInstallNewModifiersNoTool(self):
        # make sure there are no errors if the tool is missing
        self.portal._delObject('portal_modifier')
        installNewModifiers(self.portal, [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v2_5_0))
    suite.addTest(makeSuite(TestMigrations_v2_5_1))
    suite.addTest(makeSuite(TestMigrations_v2_5_2))
    suite.addTest(makeSuite(TestMigrations_v2_5_x))
    suite.addTest(makeSuite(TestMigrations_v2_5_4))
    suite.addTest(makeSuite(TestMigrations_v3_0_Actions))
    suite.addTest(makeSuite(TestMigrations_v3_0_alpha1))
    suite.addTest(makeSuite(TestMigrations_v3_0_alpha2))
    suite.addTest(makeSuite(TestMigrations_v3_0))
    return suite
