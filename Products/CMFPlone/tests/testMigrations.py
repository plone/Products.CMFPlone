#
# Tests for migration components
#

import os
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
from Products.CMFPlacefulWorkflow.interfaces import IPlacefulMarker
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

from Products.CMFPlone.migrations.v2_1.final_two11 import reindexPathIndex
from Products.CMFPlone.migrations.v2_1.two11_two12 import removeCMFTopicSkinLayer
from Products.CMFPlone.migrations.v2_1.two11_two12 import addRenameObjectButton
from Products.CMFPlone.migrations.v2_1.two11_two12 import removeDiscussionItemWorkflow
from Products.CMFPlone.migrations.v2_1.two11_two12 import addMemberData
from Products.CMFPlone.migrations.v2_1.two11_two12 import reinstallPortalTransforms

from Products.CMFPlone.migrations.v2_1.two12_two13 import normalizeNavtreeProperties
from Products.CMFPlone.migrations.v2_1.two12_two13 import removeVcXMLRPC
from Products.CMFPlone.migrations.v2_1.two12_two13 import addActionDropDownMenuIcons

from Products.CMFPlone.migrations.v2_5.alphas import installPlacefulWorkflow
from Products.CMFPlone.migrations.v2_5.alphas import installDeprecated
from Products.CMFPlone.migrations.v2_5.alphas import installPlonePAS

from Products.CMFPlone.migrations.v2_5.betas import addGetEventTypeIndex
from Products.CMFPlone.migrations.v2_5.betas import fixHomeAction
from Products.CMFPlone.migrations.v2_5.betas import removeBogusSkin
from Products.CMFPlone.migrations.v2_5.betas import addPloneSkinLayers
from Products.CMFPlone.migrations.v2_5.betas import installPortalSetup
from Products.CMFPlone.migrations.v2_5.betas import simplifyActions
from Products.CMFPlone.migrations.v2_5.betas import migrateCSSRegExpression

from Products.CMFPlone.migrations.v2_5.final_two51 import removePloneCssFromRR
from Products.CMFPlone.migrations.v2_5.final_two51 import addEventRegistrationJS
from Products.CMFPlone.migrations.v2_5.final_two51 import fixupPloneLexicon
from Products.CMFPlone.migrations.v2_5.final_two51 import fixObjDeleteAction

from Products.CMFPlone.migrations.v2_5.two51_two52 import setLoginFormInCookieAuth
from Products.CMFPlone.migrations.v2_5.two52_two53 import addMissingMimeTypes
from Products.CMFPlone.migrations.v2_5.two53_two54 import addGSSteps
from Products.CMFPlone.migrations.v2_5.two53_two54 import PROF_ID

from Products.CMFPlone.migrations.v3_0.alphas import enableZope3Site
from Products.CMFPlone.migrations.v3_0.alphas import migrateOldActions
from Products.CMFPlone.migrations.v3_0.alphas import addNewCSSFiles
from Products.CMFPlone.migrations.v3_0.alphas import addDefaultAndForbiddenContentTypesProperties
from Products.CMFPlone.migrations.v3_0.alphas import addMarkupConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import addIconForMarkupConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import updateActionsI18NDomain
from Products.CMFPlone.migrations.v3_0.alphas import updateFTII18NDomain
from Products.CMFPlone.migrations.v3_0.alphas import convertLegacyPortlets
from Products.CMFPlone.migrations.v3_0.alphas import addIconForCalendarSettingsConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import addCalendarConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import addMaintenanceConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import updateSearchAndMailHostConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import addFormTabbingJS
from Products.CMFPlone.migrations.v3_0.alphas import addFormInputLabelJS
from Products.CMFPlone.migrations.v3_0.alphas import registerToolsAsUtilities
from Products.CMFPlone.migrations.v3_0.alphas import installKss
from Products.CMFPlone.migrations.v3_0.alphas import installRedirectorUtility
from Products.CMFPlone.migrations.v3_0.alphas import addContentRulesAction
from Products.CMFPlone.migrations.v3_0.alphas import addReaderAndEditorRoles
from Products.CMFPlone.migrations.v3_0.alphas import migrateLocalroleForm
from Products.CMFPlone.migrations.v3_0.alphas import reorderUserActions
from Products.CMFPlone.migrations.v3_0.alphas import updateRtlCSSexpression
from Products.CMFPlone.migrations.v3_0.alphas import addMaintenanceProperty
from Products.CMFPlone.migrations.v3_0.alphas import addLinkIntegritySwitch
from Products.CMFPlone.migrations.v3_0.alphas import installS5
from Products.CMFPlone.migrations.v3_0.alphas import addTableContents
from Products.CMFPlone.migrations.v3_0.alphas import updatePASPlugins
from Products.CMFPlone.migrations.v3_0.alphas import updateSkinsAndSiteConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import updateConfigletTitles
from Products.CMFPlone.migrations.v3_0.alphas import addIconsForFilterAndSecurityConfiglets
from Products.CMFPlone.migrations.v3_0.alphas import addFilterAndSecurityConfiglets
from Products.CMFPlone.migrations.v3_0.alphas import addSitemapProperty
from Products.CMFPlone.migrations.v3_0.alphas import updateKukitJS
from Products.CMFPlone.migrations.v3_0.alphas import addCacheForResourceRegistry
from Products.CMFPlone.migrations.v3_0.alphas import removeHideAddItemsJS
from Products.CMFPlone.migrations.v3_0.alphas import addWebstatsJSProperty
from Products.CMFPlone.migrations.v3_0.alphas import addWebstatsJSFile
from Products.CMFPlone.migrations.v3_0.alphas import removeTablelessSkin
from Products.CMFPlone.migrations.v3_0.alphas import installContentRulesUtility
from Products.CMFPlone.migrations.v3_0.alphas import addIconForContentRulesConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import addContentRulesConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import addObjectProvidesIndex
from Products.CMFPlone.migrations.v3_0.alphas import addExternalLinksOpenNewWindowProperty
from Products.CMFPlone.migrations.v3_0.alphas import addTypesConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import addIconForTypesConfiglet
from Products.CMFPlone.migrations.v3_0.alphas import addMissingWorkflows
from Products.CMFPlone.migrations.v3_0.alphas import addManyGroupsProperty
from Products.CMFPlone.migrations.v3_0.alphas import restorePloneTool
from Products.CMFPlone.migrations.v3_0.alphas import installI18NUtilities
from Products.CMFPlone.migrations.v3_0.alphas import installProduct
from Products.CMFPlone.migrations.v3_0.alphas import addEmailCharsetProperty

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

from Products.CMFPlone.migrations.v3_1.betas import reinstallCMFPlacefulWorkflow
from Products.CMFPlone.setuphandlers import replace_local_role_manager

from five.localsitemanager.registry import FiveVerifyingAdapterLookup

from zope.app.cache.interfaces.ram import IRAMCache
from zope.app.component.hooks import clearSite
from zope.app.component.interfaces import ISite
from zope.component import getGlobalSiteManager
from zope.component import getSiteManager
from zope.component import getUtility, getMultiAdapter, queryUtility
from zope.interface import noLongerProvides

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

from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from Products.PlonePAS.interfaces.plugins import ILocalRolesPlugin

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


class TestMigrations_v2_1_1(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.icons = self.portal.portal_actionicons
        self.properties = self.portal.portal_properties
        self.memberdata = self.portal.portal_memberdata
        self.membership = self.portal.portal_membership
        self.catalog = self.portal.portal_catalog
        self.groups = self.portal.portal_groups
        self.factory = self.portal.portal_factory
        self.portal_memberdata = self.portal.portal_memberdata
        self.cp = self.portal.portal_controlpanel
        self.skins = self.portal.portal_skins

    def testReindexPathIndex(self):
        # Should reindex the path index to create new index structures
        orig_results = self.catalog(path={'query':'news', 'level':1})
        orig_len = len(orig_results)
        self.failUnless(orig_len)
        # Simulate the old EPI
        delattr(self.catalog.Indexes['path'], '_index_parents')
        self.assertRaises(AttributeError, self.catalog,
                                        {'path':{'query':'/','navtree':1}})
        reindexPathIndex(self.portal, [])
        results = self.catalog(path={'query':'news', 'level':1})
        self.assertEqual(len(results), orig_len)

    def testReindexPathIndexTwice(self):
        # Should not fail when migrated twice, should do nothing if already
        # migrated
        orig_results = self.catalog(path={'query':'news', 'level':1})
        orig_len = len(orig_results)
        self.failUnless(orig_len)
        # Simulate the old EPI
        delattr(self.catalog.Indexes['path'], '_index_parents')
        self.assertRaises(AttributeError, self.catalog,
                                        {'path':{'query':'/','navtree':1}})
        out = []
        reindexPathIndex(self.portal, out)
        # Should return a message on the first iteration
        self.failUnless(out)
        out = []
        reindexPathIndex(self.portal, out)
        results = self.catalog(path={'query':'news', 'level':1})
        self.assertEqual(len(results), orig_len)
        # should return an empty list on the second iteration because nothing
        # was done
        self.failIf(out)

    def testReindexPathIndexNoIndex(self):
        # Should not fail when index is missing
        self.catalog.delIndex('path')
        reindexPathIndex(self.portal, [])

    def testReindexPathIndexNoCatalog(self):
        # Should not fail when index is missing
        self.portal._delObject('portal_catalog')
        reindexPathIndex(self.portal, [])


class TestMigrations_v2_1_2(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.memberdata = self.portal.portal_memberdata
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.workflow = self.portal.portal_workflow

    def testRemoveCMFTopicSkinPathFromDefault(self):
        # Should remove plone_3rdParty/CMFTopic from skin paths
        self.addSkinLayer('plone_3rdParty/CMFTopic')
        removeCMFTopicSkinLayer(self.portal, [])
        path = self.skins.getSkinPath('Plone Default')
        self.failIf('plone_3rdParty/CMFTopic' in path)

    def testRemoveCMFTopicSkinTwice(self):
        # Should not fail if migrated again
        self.addSkinLayer('plone_3rdParty/CMFTopic')
        removeCMFTopicSkinLayer(self.portal, [])
        removeCMFTopicSkinLayer(self.portal, [])
        path = self.skins.getSkinPath('Plone Default')
        self.failIf('plone_3rdParty/CMFTopic' in path)

    def testRemoveCMFTopicSkinNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_skins')
        removeCMFTopicSkinLayer(self.portal, [])

    def testRemoveCMFTopicSkinPathNoLayer(self):
        # Should not fail if plone_3rdParty layer is missing
        self.removeSkinLayer('plone_3rdParty')
        removeCMFTopicSkinLayer(self.portal, [])
        path = self.skins.getSkinPath('Plone Default')
        self.failIf('plone_3rdParty/CMFTopic' in path)

    def testAddRenameObjectButton(self):
        # Should add 'rename' object_button action
        editActions = self.actions.object_buttons.objectIds()
        assert 'rename' in editActions
        self.removeActionFromTool('rename', 'object_buttons')
        addRenameObjectButton(self.portal, [])
        actions = self.actions.object_buttons.objectIds()
        self.assertEqual(sorted(actions), sorted(editActions))

    def testAddRenameObjectButtonTwice(self):
        # Should not fail if migrated again
        editActions = self.actions.object_buttons.objectIds()
        assert 'rename' in editActions
        self.removeActionFromTool('rename', 'object_buttons')
        addRenameObjectButton(self.portal, [])
        addRenameObjectButton(self.portal, [])
        actions = self.actions.object_buttons.objectIds()
        self.assertEqual(sorted(actions), sorted(editActions))

    def testAddRenameObjectButtonActionExists(self):
        # Should add 'rename' object_button action
        editActions = self.actions.object_buttons.objectIds()
        assert 'rename' in editActions
        addRenameObjectButton(self.portal, [])
        actions = self.actions.object_buttons.objectIds()
        self.assertEqual(sorted(actions), sorted(editActions))

    def testAddRenameObjectButtonNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_actions')
        addRenameObjectButton(self.portal, [])

    def testAddSEHighLightJS(self):
        jsreg = self.portal.portal_javascripts
        script_ids = jsreg.getResourceIds()
        self.failUnless('se-highlight.js' in script_ids)
        # if highlightsearchterms.js is available se-highlight.js
        # should be positioned right underneath it
        if 'highlightsearchterms.js' in script_ids:
            posSE = jsreg.getResourcePosition('se-highlight.js')
            posHST = jsreg.getResourcePosition('highlightsearchterms.js')
            self.failUnless((posSE - 1) == posHST)

    def testRemoveDiscussionItemWorkflow(self):
        self.workflow.setChainForPortalTypes(('Discussion Item',), ('(Default)',))
        removeDiscussionItemWorkflow(self.portal, [])
        self.assertEqual(self.workflow.getChainForPortalType('Discussion Item'), ())

    def testRemoveDiscussionItemWorkflowNoTool(self):
        self.portal._delObject('portal_workflow')
        removeDiscussionItemWorkflow(self.portal, [])

    def testRemoveDiscussionItemWorkflowNoType(self):
        self.types._delObject('Discussion Item')
        removeDiscussionItemWorkflow(self.portal, [])

    def testRemoveDiscussionItemWorkflowTwice(self):
        self.workflow.setChainForPortalTypes(('Discussion Item',), ('(Default)',))
        removeDiscussionItemWorkflow(self.portal, [])
        self.assertEqual(self.workflow.getChainForPortalType('Discussion Item'), ())
        removeDiscussionItemWorkflow(self.portal, [])
        self.assertEqual(self.workflow.getChainForPortalType('Discussion Item'), ())

    def testAddMustChangePassword(self):
        # Should add the 'must change password' property
        self.removeMemberdataProperty('must_change_password')
        self.failIf(self.memberdata.hasProperty('must_change_password'))
        addMemberData(self.portal, [])
        self.failUnless(self.memberdata.hasProperty('must_change_password'))

    def testAddMustChangePasswordTwice(self):
        # Should not fail if migrated again
        self.removeMemberdataProperty('must_change_password')
        self.failIf(self.memberdata.hasProperty('must_change_password'))
        addMemberData(self.portal, [])
        addMemberData(self.portal, [])
        self.failUnless(self.memberdata.hasProperty('must_change_password'))

    def testAddMustChangePasswordNoTool(self):
        # Should not fail if portal_memberdata is missing
        self.portal._delObject('portal_memberdata')
        addMemberData(self.portal, [])

    def testReinstallPortalTransforms(self):
        self.portal._delObject('portal_transforms')
        reinstallPortalTransforms(self.portal, [])
        self.failUnless(hasattr(self.portal.aq_base, 'portal_transforms'))

    def testReinstallPortalTransformsTwice(self):
        self.portal._delObject('portal_transforms')
        reinstallPortalTransforms(self.portal, [])
        reinstallPortalTransforms(self.portal, [])
        self.failUnless(hasattr(self.portal.aq_base, 'portal_transforms'))

    def testReinstallPortalTransformsNoTool(self):
        self.portal._delObject('portal_quickinstaller')
        reinstallPortalTransforms(self.portal, [])


class TestMigrations_v2_1_3(MigrationTest):

    def testNormalizeNavtreeProperties(self):
        ntp = self.portal.portal_properties.navtree_properties
        toRemove = ['skipIndex_html', 'showMyUserFolderOnly', 'showFolderishSiblingsOnly',
                    'showFolderishChildrenOnly', 'showNonFolderishObject', 'showTopicResults',
                    'rolesSeeContentView', 'rolesSeeUnpublishedContent', 'batchSize',
                    'croppingLength', 'forceParentsInBatch', 'rolesSeeHiddenContent', 'typesLinkToFolderContents']
        toAdd = {'name' : '', 'root' : '/', 'currentFolderOnlyInNavtree' : False}
        for property in toRemove:
            ntp._setProperty(property, 'X', 'string')
        for property, value in toAdd.items():
            ntp._delProperty(property)
        ntp.manage_changeProperties(bottomLevel = 65535)
        normalizeNavtreeProperties(self.portal, [])
        for property in toRemove:
            self.assertEqual(ntp.getProperty(property, None), None)
        for property, value in toAdd.items():
            self.assertEqual(ntp.getProperty(property), value)
        self.assertEqual(ntp.getProperty('bottomLevel'), 0)

    def testNormalizeNavtreePropertiesTwice(self):
        ntp = self.portal.portal_properties.navtree_properties
        toRemove = ['skipIndex_html', 'showMyUserFolderOnly', 'showFolderishSiblingsOnly',
                    'showFolderishChildrenOnly', 'showNonFolderishObject', 'showTopicResults',
                    'rolesSeeContentView', 'rolesSeeUnpublishedContent', 'rolesSeeContentsView',
                    'batchSize', 'sortCriteria', 'croppingLength', 'forceParentsInBatch',
                    'rolesSeeHiddenContent', 'typesLinkToFolderContents']
        toAdd = {'name' : '', 'root' : '/', 'currentFolderOnlyInNavtree' : False}
        for property in toRemove:
            ntp._setProperty(property, 'X', 'string')
        for property, value in toAdd.items():
            ntp._delProperty(property)
        ntp.manage_changeProperties(bottomLevel = 65535)
        normalizeNavtreeProperties(self.portal, [])
        normalizeNavtreeProperties(self.portal, [])
        for property in toRemove:
            self.assertEqual(ntp.getProperty(property, None), None)
        for property, value in toAdd.items():
            self.assertEqual(ntp.getProperty(property), value)
        self.assertEqual(ntp.getProperty('bottomLevel'), 0)

    def testNormalizeNavtreePropertiesNoTool(self):
        self.portal._delObject('portal_properties')
        normalizeNavtreeProperties(self.portal, [])

    def testNormalizeNavtreePropertiesNoSheet(self):
        self.portal.portal_properties._delObject('navtree_properties')
        normalizeNavtreeProperties(self.portal, [])

    def testNormalizeNavtreePropertiesNoPropertyToRemove(self):
        ntp = self.portal.portal_properties.navtree_properties
        if ntp.getProperty('skipIndex_html', None) is not None:
            ntp._delProperty('skipIndex_html')
        normalizeNavtreeProperties(self.portal, [])

    def testNormalizeNavtreePropertiesNewPropertyExists(self):
        ntp = self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(root = '/foo', bottomLevel = 10)
        normalizeNavtreeProperties(self.portal, [])
        self.assertEqual(ntp.getProperty('root'), '/foo')
        self.assertEqual(ntp.getProperty('bottomLevel'), 10)

    def testRemoveVcXMLRPC(self):
        # Should unregister vcXMLRPC.js
        self.addResourceToJSTool('vcXMLRPC.js')
        removeVcXMLRPC(self.portal, [])
        jsreg = self.portal.portal_javascripts
        script_ids = jsreg.getResourceIds()
        self.failIf('vcXMLRPC.js' in script_ids)

    def testRemoveVcXMLRPCTwice(self):
        # Should not fail if migrated again
        self.addResourceToJSTool('vcXMLRPC.js')
        removeVcXMLRPC(self.portal, [])
        removeVcXMLRPC(self.portal, [])
        jsreg = self.portal.portal_javascripts
        script_ids = jsreg.getResourceIds()
        self.failIf('vcXMLRPC.js' in script_ids)

    def testRemoveVcXMLRPCNoTool(self):
        # Should not break if javascripts tool is missing
        self.portal._delObject('portal_javascripts')
        removeVcXMLRPC(self.portal, [])

    def testAddActionDropDownMenuIcons(self):
        # Should add icons to object buttons
        self.removeActionIconFromTool('cut', 'object_buttons')
        self.removeActionIconFromTool('copy', 'object_buttons')
        self.removeActionIconFromTool('paste', 'object_buttons')
        self.removeActionIconFromTool('delete', 'object_buttons')
        addActionDropDownMenuIcons(self.portal, [])
        ai=self.portal.portal_actionicons
        icons = dict([
            ((x.getCategory(), x.getActionId()), x)
            for x in ai.listActionIcons()
        ])
        self.failIf(('object_buttons', 'cut') not in icons)
        self.failIf(('object_buttons', 'copy') not in icons)
        self.failIf(('object_buttons', 'paste') not in icons)
        self.failIf(('object_buttons', 'delete') not in icons)
        self.assertEqual(icons[('object_buttons', 'cut')].getExpression(), 'cut_icon.gif')
        self.assertEqual(icons[('object_buttons', 'copy')].getExpression(), 'copy_icon.gif')
        self.assertEqual(icons[('object_buttons', 'paste')].getExpression(), 'paste_icon.gif')
        self.assertEqual(icons[('object_buttons', 'delete')].getExpression(), 'delete_icon.gif')
        self.assertEqual(icons[('object_buttons', 'cut')].getTitle(), 'Cut')
        self.assertEqual(icons[('object_buttons', 'copy')].getTitle(), 'Copy')
        self.assertEqual(icons[('object_buttons', 'paste')].getTitle(), 'Paste')
        self.assertEqual(icons[('object_buttons', 'delete')].getTitle(), 'Delete')

    def testAddActionDropDownMenuIconsTwice(self):
        # Should not fail if migrated again
        self.removeActionIconFromTool('cut', 'object_buttons')
        self.removeActionIconFromTool('copy', 'object_buttons')
        self.removeActionIconFromTool('paste', 'object_buttons')
        self.removeActionIconFromTool('delete', 'object_buttons')
        addActionDropDownMenuIcons(self.portal, [])
        addActionDropDownMenuIcons(self.portal, [])
        ai=self.portal.portal_actionicons
        icons = dict([
            ((x.getCategory(), x.getActionId()), x)
            for x in ai.listActionIcons()
        ])
        self.failIf(('object_buttons', 'cut') not in icons)
        self.failIf(('object_buttons', 'copy') not in icons)
        self.failIf(('object_buttons', 'paste') not in icons)
        self.failIf(('object_buttons', 'delete') not in icons)
        self.assertEqual(icons[('object_buttons', 'cut')].getExpression(), 'cut_icon.gif')
        self.assertEqual(icons[('object_buttons', 'copy')].getExpression(), 'copy_icon.gif')
        self.assertEqual(icons[('object_buttons', 'paste')].getExpression(), 'paste_icon.gif')
        self.assertEqual(icons[('object_buttons', 'delete')].getExpression(), 'delete_icon.gif')
        self.assertEqual(icons[('object_buttons', 'cut')].getTitle(), 'Cut')
        self.assertEqual(icons[('object_buttons', 'copy')].getTitle(), 'Copy')
        self.assertEqual(icons[('object_buttons', 'paste')].getTitle(), 'Paste')
        self.assertEqual(icons[('object_buttons', 'delete')].getTitle(), 'Delete')

    def testAddActionDropDownMenuIconsNoTool(self):
        # Should not break if actionicons tool is missing
        self.portal._delObject('portal_actionicons')
        addActionDropDownMenuIcons(self.portal, [])


class TestMigrations_v2_5(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.memberdata = self.portal.portal_memberdata
        self.catalog = self.portal.portal_catalog
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.workflow = self.portal.portal_workflow

    def testInstallPlacefulWorkflow(self):
        if 'portal_placefulworkflow' in self.portal.objectIds():
            self.portal._delObject('portal_placeful_workflow')
        installPlacefulWorkflow(self.portal, [])
        self.failUnless('portal_placeful_workflow' in self.portal.objectIds())

    def testInstallPlacefulWorkflowTwice(self):
        if 'portal_placefulworkflow' in self.portal.objectIds():
            self.portal._delObject('portal_placeful_workflow')
        installPlacefulWorkflow(self.portal, [])
        installPlacefulWorkflow(self.portal, [])
        self.failUnless('portal_placeful_workflow' in self.portal.objectIds())

    def testInstallPortalSetup(self):
        if 'portal_setup' in self.portal.objectIds():
            self.portal._delObject('portal_setup')
        installPortalSetup(self.portal, [])
        self.failUnless('portal_setup' in self.portal.objectIds())

    def testInstallPortalSetupTwice(self):
        if 'portal_setup' in self.portal.objectIds():
            self.portal._delObject('portal_setup')
        installPortalSetup(self.portal, [])
        installPortalSetup(self.portal, [])
        self.failUnless('portal_setup' in self.portal.objectIds())

    def testInstallPlonePAS(self):
        qi = self.portal.portal_quickinstaller
        if qi.isProductInstalled('PlonePAS'):
            self.setRoles(('Manager',))
            qi.uninstallProducts(['PlonePAS'])
        self.failIf(qi.isProductInstalled('PlonePAS'))
        installPlonePAS(self.portal, [])
        self.failUnless(qi.isProductInstalled('PlonePAS'))

    def testInstallPlonePASTwice(self):
        qi = self.portal.portal_quickinstaller
        if qi.isProductInstalled('PlonePAS'):
            self.setRoles(('Manager',))
            qi.uninstallProducts(['PlonePAS'])
        installPlonePAS(self.portal, [])
        installPlonePAS(self.portal, [])
        self.failUnless(qi.isProductInstalled('PlonePAS'))

    def testInstallPlonePASWithEnvironmentVariableSet(self):
        qi = self.portal.portal_quickinstaller
        if qi.isProductInstalled('PlonePAS'):
            self.setRoles(('Manager',))
            qi.uninstallProducts(['PlonePAS'])
        self.failIf(qi.isProductInstalled('PlonePAS'))
        os.environ['SUPPRESS_PLONEPAS_INSTALLATION'] = 'YES'
        installPlonePAS(self.portal, [])
        self.failIf(qi.isProductInstalled('PlonePAS'))
        del os.environ['SUPPRESS_PLONEPAS_INSTALLATION']
        installPlonePAS(self.portal, [])
        self.failUnless(qi.isProductInstalled('PlonePAS'))

    def testInstallDeprecated(self):
        # Remove skin
        self.skins._delObject('plone_deprecated')
        skins = ['Plone Default']
        for s in skins:
            path = self.skins.getSkinPath(s)
            path = [p.strip() for p in  path.split(',')]
            path.remove('plone_deprecated')
            self.skins.addSkinSelection(s, ','.join(path))
        self.failIf('plone_deprecated' in
                           self.skins.getSkinPath('Plone Default').split(','))
        installDeprecated(self.portal, [])
        self.failUnless('plone_deprecated' in self.skins.objectIds())
        # it should be in the skin now
        self.assertEqual(self.skins.getSkinPath('Plone Default').split(',')[-3],
                         'plone_deprecated')

    def testInstallDeprecatedTwice(self):
        # Remove skin
        self.skins._delObject('plone_deprecated')
        skins = ['Plone Default']
        for s in skins:
            path = self.skins.getSkinPath(s)
            path = [p.strip() for p in  path.split(',')]
            path.remove('plone_deprecated')
            self.skins.addSkinSelection(s, ','.join(path))
        self.failIf('plone_deprecated' in
                           self.skins.getSkinPath('Plone Default').split(','))
        skin_len = len(self.skins.getSkinPath('Plone Default').split(','))
        installDeprecated(self.portal, [])
        installDeprecated(self.portal, [])
        self.failUnless('plone_deprecated' in self.skins.objectIds())
        # it should be in the skin now
        self.assertEqual(self.skins.getSkinPath('Plone Default').split(',')[-3],
                         'plone_deprecated')
        self.assertEqual(len(self.skins.getSkinPath('Plone Default').split(',')),
                         skin_len+1)

    def testInstallDeprecatedNoTool(self):
        # Remove skin
        self.portal._delObject('portal_skins')
        installDeprecated(self.portal, [])

    def testAddDragDropReorderJS(self):
        jsreg = self.portal.portal_javascripts
        script_ids = jsreg.getResourceIds()
        self.failUnless('dragdropreorder.js' in script_ids)
        # if dropdown.js is available dragdropreorder.js
        # should be positioned right underneath it
        if 'dropdown.js' in script_ids:
            posSE = jsreg.getResourcePosition('dragdropreorder.js')
            posHST = jsreg.getResourcePosition('select_all.js')
            self.failUnless((posSE - 1) == posHST)

    def testAddGetEventTypeIndex(self):
        # Should add getEventType index
        self.catalog.delIndex('getEventType')
        addGetEventTypeIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('getEventType')
        self.assertEqual(index.__class__.__name__, 'KeywordIndex')

    def testAddGetEventTypeIndexTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('getEventType')
        addGetEventTypeIndex(self.portal, [])
        addGetEventTypeIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('getEventType')
        self.assertEqual(index.__class__.__name__, 'KeywordIndex')

    def testAddGetEventTypeIndexNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        addGetEventTypeIndex(self.portal, [])

    def testFixHomeAction(self):
        editActions = ('index_html',)
        for a in editActions:
            self.removeActionFromTool(a)
        fixHomeAction(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixHomeActionTwice(self):
        editActions = ('index_html',)
        for a in editActions:
            self.removeActionFromTool(a)
        fixHomeAction(self.portal, [])
        fixHomeAction(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixHomeActionNoTool(self):
        self.portal._delObject('portal_actions')
        fixHomeAction(self.portal, [])

    def testRemoveBogusSkin(self):
        # Add bogus skin
        self.skins.manage_skinLayers(add_skin=1, skinname='cmf_legacy',
                                  skinpath=['plone_forms','plone_templates'])
        self.failUnless(self.skins._getSelections().has_key('cmf_legacy'))
        removeBogusSkin(self.portal, [])
        # It should be gone
        self.failIf(self.skins._getSelections().has_key('cmf_legacy'))

    def testAddPloneSkinLayers(self):
        # Add bogus skin
        self.skins.manage_skinLayers(add_skin=1, skinname='foo_bar',
                                  skinpath=['plone_forms','plone_templates'])
        self.failUnless(self.skins._getSelections().has_key('foo_bar'))

        path = [p.strip() for p in self.skins.getSkinPath('foo_bar').split(',')]
        self.assertEqual(['plone_forms', 'plone_templates'], path)

        addPloneSkinLayers(self.portal, [])

        path = [p.strip() for p in self.skins.getSkinPath('foo_bar').split(',')]
        self.assertEqual(['plone_forms', 'plone_templates', 'plone_deprecated'], path)

    def testRemoveBogusSkinTwice(self):
        self.skins.manage_skinLayers(add_skin=1, skinname='cmf_legacy',
                                  skinpath=['plone_forms','plone_templates'])
        self.failUnless(self.skins._getSelections().has_key('cmf_legacy'))
        removeBogusSkin(self.portal, [])
        removeBogusSkin(self.portal, [])
        self.failIf(self.skins._getSelections().has_key('cmf_legacy'))

    def testRemoveBogusSkinNoSkin(self):
        self.failIf(self.skins._getSelections().has_key('cmf_legacy'))
        removeBogusSkin(self.portal, [])
        self.failIf(self.skins._getSelections().has_key('cmf_legacy'))

    def testRemoveBogusSkinNoTool(self):
        self.portal._delObject('portal_skins')
        removeBogusSkin(self.portal, [])

    def testSimplifyActions(self):
        # Should simplify a number of actions across multiple tools using the
        # view methods
        tool = self.portal.portal_actions
        paste = tool.object_buttons.paste
        rename = tool.object_buttons.rename
        contents = tool.object.folderContents
        index = tool.portal_tabs.index_html
        # Set the expressions and conditions to their 2.5 analogues to test
        # every substitution
        paste._updateProperty('url_expr',
                'python:"%s/object_paste"%((object.isDefaultPageInFolder() or not object.is_folderish()) and object.getParentNode().absolute_url() or object_url)')
        rename._updateProperty('url_expr',
                'python:"%s/object_rename"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)')
        rename.edit('available_expr',
                'python:portal.portal_membership.checkPermission("Delete objects", object.aq_inner.getParentNode()) and portal.portal_membership.checkPermission("Copy or Move", object) and portal.portal_membership.checkPermission("Add portal content", object) and object is not portal and not (object.isDefaultPageInFolder() and object.getParentNode() is portal)')
        contents._updateProperty('url_expr',
                "python:((object.isDefaultPageInFolder() and object.getParentNode().absolute_url()) or folder_url)+'/folder_contents'")
        index._updateProperty('url_expr',
                'string: ${here/@@plone/navigationRootUrl}')

        # Verify that the changes have been made
        paste = tool.object_buttons.paste
        self.failUnless("object.isDefaultPageInFolder()" in
                                                  paste.getProperty('url_expr'))
        # Run the action simplifications
        simplifyActions(self.portal, [])
        self.assertEqual(paste.getProperty('url_expr'),
                "string:${globals_view/getCurrentFolderUrl}/object_paste")
        self.assertEqual(rename.getProperty('url_expr'),
                "string:${globals_view/getCurrentObjectUrl}/object_rename")
        self.assertEqual(rename.getProperty('available_expr'),
                'python:checkPermission("Delete objects", globals_view.getParentObject()) and checkPermission("Copy or Move", object) and checkPermission("Add portal content", object) and not globals_view.isPortalOrPortalDefaultPage()')
        self.assertEqual(contents.getProperty('url_expr'),
                "string:${globals_view/getCurrentFolderUrl}/folder_contents")
        self.assertEqual(index.getProperty('url_expr'),
                "string:${globals_view/navigationRootUrl}")

    def testSimplifyActionsTwice(self):
        # Should result in the same string when applied twice
        tool = self.portal.portal_actions
        paste = tool.object_buttons.paste
        paste._updateProperty('url_expr',
                              'python:"%s/object_paste"%((object.isDefaultPageInFolder() or not object.is_folderish()) and object.getParentNode().absolute_url() or object_url)')

        # Verify that the changes have been made
        paste = tool.object_buttons.paste
        self.failUnless("object.isDefaultPageInFolder()" in
                                paste.getProperty('url_expr'))

        # Run the action simplifications twice
        simplifyActions(self.portal, [])
        simplifyActions(self.portal, [])

        # We should have the same result
        self.assertEqual(paste.getProperty('url_expr'),
                "string:${globals_view/getCurrentFolderUrl}/object_paste")

    def testSimplifyActionsNoTool(self):
        # Sholud not fail if the tool is missing
        self.portal._delObject('portal_actions')
        simplifyActions(self.portal, [])

    def testMigrateCSSRegExpression(self):
        # Should convert the expression using a deprecated script to use the
        # view
        css_reg = self.portal.portal_css
        resource = css_reg.getResource('RTL.css')
        resource.setExpression("python:object.isRightToLeft(domain='plone')")
        css_reg.cookResources()

        # Ensure the change worked
        resource = css_reg.getResource('RTL.css')
        self.failUnless('object.isRightToLeft' in resource.getExpression())

        # perform the migration
        migrateCSSRegExpression(self.portal, [])
        self.assertEqual(resource.getExpression(),
                "object/@@plone/isRightToLeft")

    def testMigrateCSSRegExpressionWith25Expression(self):
        # Should replace the restrictedTraverse call with the more compact
        # path expression
        css_reg = self.portal.portal_css
        resource = css_reg.getResource('RTL.css')
        resource.setExpression(
"python:object.restrictedTraverse('@@plone').isRightToLeft(domain='plone')")
        css_reg.cookResources()

        # perform the migration
        migrateCSSRegExpression(self.portal, [])
        self.assertEqual(resource.getExpression(),
                "object/@@plone/isRightToLeft")

    def testMigrateCSSRegExpressionTwice(self):
        # Should result in the same string when applied twice
        css_reg = self.portal.portal_css
        resource = css_reg.getResource('RTL.css')
        resource.setExpression("python:object.isRightToLeft(domain='plone')")
        css_reg.cookResources()

        # perform the migration twice
        migrateCSSRegExpression(self.portal, [])
        migrateCSSRegExpression(self.portal, [])
        self.assertEqual(resource.getExpression(),
                "object/@@plone/isRightToLeft")

    def testMigrateCSSRegExpressionNoTool(self):
        # Should not fail if the tool is missing
        self.portal._delObject('portal_css')
        migrateCSSRegExpression(self.portal, [])

    def testMigrateCSSRegExpressionNoResource(self):
        # Should not fail if the resource is missing
        css_reg = self.portal.portal_css
        css_reg.unregisterResource('RTL.css')
        migrateCSSRegExpression(self.portal, [])

class TestMigrations_v2_5_1(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.memberdata = self.portal.portal_memberdata
        self.catalog = self.portal.portal_catalog
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.workflow = self.portal.portal_workflow
        self.css = self.portal.portal_css

    def testRemovePloneCssFromRR(self):
        # Check to ensure that plone.css gets removed from portal_css
        self.css.registerStylesheet('plone.css', media='all')
        self.failUnless('plone.css' in self.css.getResourceIds())
        removePloneCssFromRR(self.portal, [])
        self.failIf('plone.css' in self.css.getResourceIds())

    def testRemovePloneCssFromRRTwice(self):
        # Should not fail if performed twice
        self.css.registerStylesheet('plone.css', media='all')
        self.failUnless('plone.css' in self.css.getResourceIds())
        removePloneCssFromRR(self.portal, [])
        removePloneCssFromRR(self.portal, [])
        self.failIf('plone.css' in self.css.getResourceIds())

    def testRemovePloneCssFromRRNoCSS(self):
        # Should not fail if the stylesheet is missing
        self.failIf('plone.css' in self.css.getResourceIds())
        removePloneCssFromRR(self.portal, [])

    def testRemovePloneCssFromRRNoTool(self):
        # Should not fail if the tool is missing
        self.portal._delObject('portal_css')
        removePloneCssFromRR(self.portal, [])

    def testAddEventRegistrationJS(self):
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('event-registration.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('event-registration.js' in script_ids)
        # migrate and test again
        addEventRegistrationJS(self.portal, [])
        script_ids = jsreg.getResourceIds()
        self.failUnless('event-registration.js' in script_ids)
        self.assertEqual(jsreg.getResourcePosition('event-registration.js'), 0)

    def testAddEventRegistrationJSTwice(self):
        # Should not break if migrated again
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('event-registration.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('event-registration.js' in script_ids)
        # migrate and test again
        addEventRegistrationJS(self.portal, [])
        addEventRegistrationJS(self.portal, [])
        script_ids = jsreg.getResourceIds()
        self.failUnless('event-registration.js' in script_ids)
        self.assertEqual(jsreg.getResourcePosition('event-registration.js'), 0)

    def testAddEventRegistrationJSNoTool(self):
        # Should not break if the tool is missing
        self.portal._delObject('portal_javascripts')
        addEventRegistrationJS(self.portal, [])

    def testFixupPloneLexicon(self):
        # Should update the plone_lexicon pipeline
        lexicon = self.portal.portal_catalog.plone_lexicon
        lexicon._pipeline = (object(), object())
        fixupPloneLexicon(self.portal, [])
        self.failUnless(isinstance(lexicon._pipeline[0], Splitter))
        self.failUnless(isinstance(lexicon._pipeline[1], CaseNormalizer))

    def testFixupPloneLexiconTwice(self):
        # Should not break if migrated again
        lexicon = self.portal.portal_catalog.plone_lexicon
        lexicon._pipeline = (object(), object())
        fixupPloneLexicon(self.portal, [])
        fixupPloneLexicon(self.portal, [])
        self.failUnless(isinstance(lexicon._pipeline[0], Splitter))
        self.failUnless(isinstance(lexicon._pipeline[1], CaseNormalizer))

    def testFixupPloneLexiconNoLexicon(self):
        # Should not break if plone_lexicon is missing
        self.portal.portal_catalog._delObject('plone_lexicon')
        fixupPloneLexicon(self.portal, [])

    def testFixupPloneLexiconNoTool(self):
        # Should not break if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        fixupPloneLexicon(self.portal, [])

    def tesFixObjDeleteActionTwice(self):
        # Should not error if performed twice
        editActions = ('delete',)
        for a in editActions:
            self.removeActionFromTool(a)
        fixObjDeleteAction(self.portal, [])
        fixObjDeleteAction(self.portal, [])
        actions = [x.id for x in self.actions.listActions()
                   if x.id in editActions]
        # check that all of our deleted actions are now present
        for a in editActions:
            self.failUnless(a in actions)
        # ensure that they are present only once
        self.failUnlessEqual(len(editActions), len(actions))

    def testFixObjDeleteActionNoAction(self):
        # Should add the action
        editActions = ('delete',)
        for a in editActions:
            self.removeActionFromTool(a)
        fixObjDeleteAction(self.portal, [])
        actions = [x for x in self.actions.object_buttons.objectIds()
                   if x in editActions]
        for a in editActions:
            self.failUnless(a in actions)
        self.failUnlessEqual(len(editActions), len(actions))

    def testFixObjDeleteActionNoTool(self):
        self.portal._delObject('portal_actions')
        fixObjDeleteAction(self.portal, [])

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

    def testMigrateActionsTwice(self):
        self.failUnless(self.discussion._actions == (self.reply, ))

        migrateOldActions(self.portal, [])
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

        updateActionsI18NDomain(self.portal, [])
        
        self.assertEquals(reply.i18n_domain, 'plone')

    def testUpdateActionsI18NDomainTwice(self):
        migrateOldActions(self.portal, [])
        reply = self.actions.reply_actions.reply
        self.assertEquals(reply.i18n_domain, '')

        updateActionsI18NDomain(self.portal, [])
        updateActionsI18NDomain(self.portal, [])

        self.assertEquals(reply.i18n_domain, 'plone')

    def testUpdateActionsI18NDomainNonAscii(self):
        migrateOldActions(self.portal, [])
        reply = self.actions.reply_actions.reply
        reply.title = 'Foo\xc3'
        self.assertEquals(reply.i18n_domain, '')
        self.assertEquals(reply.title, 'Foo\xc3')

        updateActionsI18NDomain(self.portal, [])
        
        self.assertEquals(reply.i18n_domain, '')

    def testHistoryActionID(self):
        migrateHistoryTab(self.portal, [])
        objects = getattr(self.actions, 'object', None)
        self.failIf('rss' in objects.objectIds())

    def testHistoryActionIDTwice(self):
        migrateHistoryTab(self.portal, [])
        migrateHistoryTab(self.portal, [])
        objects = getattr(self.actions, 'object', None)
        self.failIf('rss' in objects.objectIds())


    def testProviderCleanup(self):
        self.actions.addActionProvider("portal_membership")
        self.failUnless("portal_membership" in self.actions.listActionProviders())
        cleanupActionProviders(self.portal, [])
        self.failIf("portal_membership" in self.actions.listActionProviders())


    def testRemovePropertiesActions(self):
        ti=self.types.getTypeInfo("Document")
        if ti.getActionObject("object/properties") is None:
            ti.addAction("metadata", "name", "action", "condition",
                    "permission", "object",)
        hidePropertiesAction(self.portal, [])
        self.failUnless(ti.getActionObject("object/metadata") is None)


    def beforeTearDown(self):
        if len(self.discussion._actions) > 0:
            self.discussion._actions = ()


class TestMigrations_v3_0(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.cp = self.portal.portal_controlpanel
        self.icons = self.portal.portal_actionicons
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.workflow = self.portal.portal_workflow
        self.properties = self.portal.portal_properties
        self.cp = self.portal.portal_controlpanel

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

        # Then run the migration step
        enableZope3Site(self.portal, [])

        # And see if we have an ISite with a local site manager
        self.failUnless(ISite.providedBy(self.portal))
        gsm = getGlobalSiteManager()
        sm = getSiteManager(self.portal)
        self.failIf(gsm is sm)
        lc = sm.utilities.LookupClass
        self.failUnless(lc == FiveVerifyingAdapterLookup)

        # Test the lookupclass migration
        sm.utilities.LookupClass = None

        enableZope3Site(self.portal, [])

        self.failUnless(sm.utilities.LookupClass == FiveVerifyingAdapterLookup)
        self.failUnless(sm.utilities.__parent__ == sm)
        self.failUnless(sm.__parent__ == self.portal)

    def testEnableZope3SiteTwice(self):
        # First we remove the site and site manager
        self.disableSite(self.portal)
        clearSite(self.portal)
        self.portal.setSiteManager(None)

        # Then run the migration step
        enableZope3Site(self.portal, [])
        enableZope3Site(self.portal, [])

        # And see if we have an ISite with a local site manager
        self.failUnless(ISite.providedBy(self.portal))
        gsm = getGlobalSiteManager()
        sm = getSiteManager(self.portal)
        self.failIf(gsm is sm)

        # Test the lookupclass migration
        sm.utilities.LookupClass = None

        enableZope3Site(self.portal, [])
        enableZope3Site(self.portal, [])

        self.failUnless(sm.utilities.LookupClass == FiveVerifyingAdapterLookup)
        self.failUnless(sm.utilities.__parent__ == sm)
        self.failUnless(sm.__parent__ == self.portal)

    def testAddNewCSSFiles(self):
        cssreg = self.portal.portal_css
        added_ids = ['navtree.css', 'invisibles.css', 'forms.css']
        for id in added_ids:
            cssreg.unregisterResource(id)
        stylesheet_ids = cssreg.getResourceIds()
        for id in added_ids:
            self.failIf('navtree.css' in stylesheet_ids)
        addNewCSSFiles(self.portal, [])
        stylesheet_ids = cssreg.getResourceIds()
        for id in added_ids:
            self.failUnless(id in stylesheet_ids)
        # perform migration twice
        addNewCSSFiles(self.portal, [])
        for id in added_ids:
            self.failUnless(id in stylesheet_ids)

    def testAddNewBeta2CSSFiles(self):
        cssreg = self.portal.portal_css
        added_ids = ['controlpanel.css']
        for id in added_ids:
            cssreg.unregisterResource(id)
        stylesheet_ids = cssreg.getResourceIds()
        for id in added_ids:
            self.failIf('controlpanel.css' in stylesheet_ids)
        loadMigrationProfile(self.portal,
                'profile-Products.CMFPlone.migrations:3.0b1-3.0b2',
                steps=["cssregistry"])
        stylesheet_ids = cssreg.getResourceIds()
        for id in added_ids:
            self.failUnless(id in stylesheet_ids)
        # perform migration twice
        loadMigrationProfile(self.portal,
                'profile-Products.CMFPlone.migrations:3.0b1-3.0b2',
                steps=["cssregistry"])
        for id in added_ids:
            self.failUnless(id in stylesheet_ids)

    def testAddDefaultAndForbiddenContentTypesProperties(self):
        # Should add the forbidden_contenttypes and default_contenttype property
        self.removeSiteProperty('forbidden_contenttypes')
        self.removeSiteProperty('default_contenttype')
        self.failIf(self.properties.site_properties.hasProperty('forbidden_contenttypes'))
        self.failIf(self.properties.site_properties.hasProperty('default_contenttype'))
        addDefaultAndForbiddenContentTypesProperties(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('forbidden_contenttypes'))
        self.failUnless(self.properties.site_properties.hasProperty('default_contenttype'))
        self.failUnless(self.properties.site_properties.forbidden_contenttypes == ( 
            'text/structured',
            'text/x-rst',
            'text/plain-pre',
            'text/x-python',
            'text/x-web-markdown',
            'text/x-web-textile',
            'text/x-web-intelligent')
        )

    def testAddDefaultAndForbiddenContentTypesPropertiesTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('forbidden_contenttypes')
        self.removeSiteProperty('default_contenttype')
        self.failIf(self.properties.site_properties.hasProperty('forbidden_contenttypes'))
        self.failIf(self.properties.site_properties.hasProperty('default_contenttype'))
        addDefaultAndForbiddenContentTypesProperties(self.portal, [])
        self.failUnless(self.properties.site_properties.forbidden_contenttypes == ( 
            'text/structured',
            'text/x-rst',
            'text/plain-pre',
            'text/x-python',
            'text/x-web-markdown',
            'text/x-web-textile',
            'text/x-web-intelligent')
        )
        self.properties.site_properties.forbidden_contenttypes = ('text/x-rst',)
        addDefaultAndForbiddenContentTypesProperties(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('forbidden_contenttypes'))
        self.failUnless(self.properties.site_properties.hasProperty('default_contenttype'))
        # adding a second time should leave existing `forbidden_contenttypes` settings alone:
        self.failUnless(self.properties.site_properties.forbidden_contenttypes == ( 
            'text/x-rst', 
            )
        )
        
    def testAddIconForMarkupConfiglet(self):
        self.removeActionIconFromTool('MarkupSettings')
        addIconForMarkupConfiglet(self.portal, [])
        self.failUnless('MarkupSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForMarkupConfigletTwice(self):
        self.removeActionIconFromTool('MarkupSettings')
        addIconForMarkupConfiglet(self.portal, [])
        addIconForMarkupConfiglet(self.portal, [])
        self.failUnless('MarkupSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForMarkupConfigletNoTool(self):
        self.portal._delObject('portal_actionicons')
        addIconForMarkupConfiglet(self.portal, [])
    
    def testAddMarkupConfiglet(self):
        self.removeActionFromTool('MarkupSettings', action_provider='portal_controlpanel')
        addMarkupConfiglet(self.portal, [])
        self.failUnless('MarkupSettings' in [action.getId() for action in self.cp.listActions()])
        types = self.cp.getActionObject('Plone/MarkupSettings')
        self.assertEquals(types.action.text,
                          'string:${portal_url}/@@markup-controlpanel')

    def testAddMarkupConfigletTwice(self):
        self.removeActionFromTool('MarkupSettings', action_provider='portal_controlpanel')
        addMarkupConfiglet(self.portal, [])
        addMarkupConfiglet(self.portal, [])
        self.failUnless('MarkupSettings' in [action.getId() for action in self.cp.listActions()])
        types = self.cp.getActionObject('Plone/MarkupSettings')
        self.assertEquals(types.action.text,
                          'string:${portal_url}/@@markup-controlpanel')
                          
    def testAddMarkupConfigletNoTool(self):
        self.portal._delObject('portal_controlpanel')
        addMarkupConfiglet(self.portal, [])
                              
    def testAddIconForTypesConfiglet(self):
        self.removeActionIconFromTool('TypesSettings')
        addIconForTypesConfiglet(self.portal, [])
        self.failUnless('TypesSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForTypesConfigletTwice(self):
        self.removeActionIconFromTool('TypesSettings')
        addIconForTypesConfiglet(self.portal, [])
        addIconForTypesConfiglet(self.portal, [])
        self.failUnless('TypesSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForTypesConfigletNoTool(self):
        self.portal._delObject('portal_actionicons')
        addIconForTypesConfiglet(self.portal, [])      
                          
    def testAddTypesConfiglet(self):
        self.removeActionFromTool('TypesSettings', action_provider='portal_controlpanel')
        addTypesConfiglet(self.portal, [])
        self.failUnless('TypesSettings' in [action.getId() for action in self.cp.listActions()])
        types = self.cp.getActionObject('Plone/TypesSettings')
        self.assertEquals(types.action.text,
                          'string:${portal_url}/@@types-controlpanel')

    def testAddTypesConfigletTwice(self):
        self.removeActionFromTool('TypesSettings', action_provider='portal_controlpanel')
        addTypesConfiglet(self.portal, [])
        addTypesConfiglet(self.portal, [])
        self.failUnless('TypesSettings' in [action.getId() for action in self.cp.listActions()])
        types = self.cp.getActionObject('Plone/TypesSettings')
        self.assertEquals(types.action.text,
                          'string:${portal_url}/@@types-controlpanel')

    def testAddTypesConfigletNoTool(self):
        self.portal._delObject('portal_controlpanel')
        addTypesConfiglet(self.portal, [])

    def testAddFormTabbingJS(self):
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('form_tabbing.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('form_tabbing.js' in script_ids)
        # migrate and test again
        addFormTabbingJS(self.portal, [])
        script_ids = jsreg.getResourceIds()
        self.failUnless('form_tabbing.js' in script_ids)
        # if collapsiblesections.js is available form_tabbing.js
        # should be positioned right underneath it
        if 'collapsiblesections.js' in script_ids:
            posSE = jsreg.getResourcePosition('form_tabbing.js')
            posHST = jsreg.getResourcePosition('collapsiblesections.js')
            self.failUnless((posSE - 1) == posHST)

    def testAddFormInputLabelJS(self):
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('input-label.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('input-label.js' in script_ids)
        # migrate and test again
        addFormInputLabelJS(self.portal, [])
        script_ids = jsreg.getResourceIds()
        self.failUnless('input-label.js' in script_ids)

    def testUpdateFTII18NDomain(self):
        doc = self.types.Document
        doc.i18n_domain = ''
        # Update FTI's
        updateFTII18NDomain(self.portal, [])
        # domain should have been updated
        self.assertEquals(doc.i18n_domain, 'plone')

    def testUpdateFTII18NDomainTwice(self):
        doc = self.types.Document
        doc.i18n_domain = ''
        # Update FTI's twice
        updateFTII18NDomain(self.portal, [])
        updateFTII18NDomain(self.portal, [])
        # domain should have been updated
        self.assertEquals(doc.i18n_domain, 'plone')

    def testUpdateFTII18NDomainNonAscii(self):
        doc = self.types.Document
        doc.i18n_domain = ''
        doc.title = 'Foo\xc3'
        # Update FTI's
        updateFTII18NDomain(self.portal, [])
        # domain should have been updated
        self.assertEquals(doc.i18n_domain, '')

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
        
    def testLegacyPortletsConvertedTwice(self):
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
        
        convertLegacyPortlets(self.portal, [])
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

    def testAddIconForCalendarSettingsConfiglet(self):
        # Should add the calendar action icon
        self.removeActionIconFromTool('CalendarSettings')
        addIconForCalendarSettingsConfiglet(self.portal, [])
        self.failUnless('CalendarSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForCalendarSettingsConfigletTwice(self):
        # Should not fail if migrated again
        self.removeActionIconFromTool('CalendarSettings')
        addIconForCalendarSettingsConfiglet(self.portal, [])
        addIconForCalendarSettingsConfiglet(self.portal, [])
        self.failUnless('CalendarSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForCalendarSettingsConfigletNoTool(self):
        # Should not fail if portal_actionicons is missing
        self.portal._delObject('portal_actionicons')
        addIconForCalendarSettingsConfiglet(self.portal, [])

    def testAddCalendarConfiglet(self):
        self.removeActionFromTool('CalendarSettings', action_provider='portal_controlpanel')
        addCalendarConfiglet(self.portal, [])
        self.failUnless('CalendarSettings' in [x.getId() for x in self.cp.listActions()])
        cal = self.cp.getActionObject('Plone/CalendarSettings')
        self.assertEquals(cal.title, 'Calendar')
        self.assertEquals(cal.action.text,
                          'string:${portal_url}/@@calendar-controlpanel')
    
    def testAddCalendarConfigletTwice(self):
        # Should not fail if done twice
        self.removeActionFromTool('CalendarSettings', action_provider='portal_controlpanel')
        addCalendarConfiglet(self.portal, [])
        addCalendarConfiglet(self.portal, [])
        self.failUnless('CalendarSettings' in [x.getId() for x in self.cp.listActions()])
        cal = self.cp.getActionObject('Plone/CalendarSettings')
        self.assertEquals(cal.title, 'Calendar')
        self.assertEquals(cal.action.text,
                          'string:${portal_url}/@@calendar-controlpanel')
    
    def testAddCalendarConfigletNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_controlpanel')
        addCalendarConfiglet(self.portal, [])

    def testUpdateSearchAndMailHostConfiglet(self):
        search = self.cp.getActionObject('Plone/SearchSettings')
        mail = self.cp.getActionObject('Plone/MailHost')
        search.action = Expression('string:search')
        mail.action = Expression('string:mail')
        updateSearchAndMailHostConfiglet(self.portal, [])
        self.assertEquals(search.title, 'Search')
        self.assertEquals(search.action.text,
                          'string:${portal_url}/@@search-controlpanel')
        self.assertEquals(mail.title, 'Mail')
        self.assertEquals(mail.action.text,
                          'string:${portal_url}/@@mail-controlpanel')
    
    def testUpdateSearchAndMailHostConfigletTwice(self):
        # Should not fail if done twice
        search = self.cp.getActionObject('Plone/SearchSettings')
        mail = self.cp.getActionObject('Plone/MailHost')
        search.action = Expression('string:search')
        mail.action = Expression('string:mail')
        updateSearchAndMailHostConfiglet(self.portal, [])
        updateSearchAndMailHostConfiglet(self.portal, [])
        self.assertEquals(search.title, 'Search')
        self.assertEquals(search.action.text,
                          'string:${portal_url}/@@search-controlpanel')
        self.assertEquals(mail.title, 'Mail')
        self.assertEquals(mail.action.text,
                          'string:${portal_url}/@@mail-controlpanel')
    
    def testUpdateSearchAndMailHostConfigletNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_controlpanel')
        updateSearchAndMailHostConfiglet(self.portal, [])

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
    
    def testInstallKss(self, unregister=True):
        'Test kss migration'
        jstool = self.portal.portal_javascripts
        csstool = self.portal.portal_css
        mt = self.portal.mimetypes_registry
        mtid = 'text/kss'
        st = self.portal.portal_skins
        skins = ['Plone Default']
        if unregister:
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
            # XXX we cannot remove the directory views, so...
        # migrate and test again
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

    def testInstallKssTwice(self):
        'Test kss migration, twice'
        self.testInstallKss()
        self.testInstallKss(unregister=False)
        
    def testInstallRedirectorUtility(self):
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IRedirectionStorage)
        installRedirectorUtility(self.portal, [])
        self.failIf(sm.queryUtility(IRedirectionStorage) is None)

    def testInstallRedirectorUtilityTwice(self):
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IRedirectionStorage)
        installRedirectorUtility(self.portal, [])
        installRedirectorUtility(self.portal, [])
        self.failIf(sm.queryUtility(IRedirectionStorage) is None)
        
    def testAddContentRulesAction(self):
        self.portal.portal_actions.object._delObject('contentrules')
        addContentRulesAction(self.portal, [])
        self.failUnless('contentrules' in self.portal.portal_actions.object.objectIds())
        
    def testAddContentRulesActionTwice(self):
        self.portal.portal_actions.object._delOb('contentrules')
        addContentRulesAction(self.portal, [])
        addContentRulesAction(self.portal, [])
        self.failUnless('contentrules' in self.portal.portal_actions.object.objectIds())
        
    def testAddContentRulesActionNoTool(self):
        self.portal._delOb('portal_actions')
        addContentRulesAction(self.portal, [])
        
    def testAddContentRulesActionNoCategory(self):
        self.portal.portal_actions._delOb('object')
        addContentRulesAction(self.portal, [])
        
    def testAddReaderEditorRoles(self):
        self.portal._delRoles(['Reader', 'Editor'])
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
        addReaderAndEditorRoles(self.portal, [])
        self.failUnless('Reader' in self.portal.valid_roles())
        self.failUnless('Editor' in self.portal.valid_roles())
        self.failUnless('Reader' in self.portal.acl_users.portal_role_manager.listRoleIds())
        self.failUnless('Editor' in self.portal.acl_users.portal_role_manager.listRoleIds())
        self.failUnless('View' in [r['name'] for r in self.portal.permissionsOfRole('Reader') if r['selected']])
        self.failUnless('Modify portal content' in [r['name'] for r in self.portal.permissionsOfRole('Editor') if r['selected']])
        
    def testAddReaderEditorRolesTwice(self):
        self.portal._delRoles(['Reader', 'Editor'])
        addReaderAndEditorRoles(self.portal, [])
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
        migrateLocalroleForm(self.portal, [])
        self.assertEquals('@@sharing', fti.getMethodAliases()['sharing'])
        test_action = fti.listActions()[-1]
        self.assertEquals('string:${object_url}/@@sharing', test_action.getActionExpression())

    def testMigrateLocalroleFormTwice(self):
        fti = self.portal.portal_types['Document']
        aliases = fti.getMethodAliases()
        aliases['sharing'] = 'folder_localrole_form'
        fti.setMethodAliases(aliases)
        fti.addAction('test', 'Test', 'string:${object_url}/folder_localrole_form', None, 'View', 'object')
        migrateLocalroleForm(self.portal, [])
        migrateLocalroleForm(self.portal, [])
        self.assertEquals('@@sharing', fti.getMethodAliases()['sharing'])
        test_action = fti.listActions()[-1]
        self.assertEquals('string:${object_url}/@@sharing', test_action.getActionExpression())
        
    def testMigrateLocalroleFormNoTool(self):
        self.portal._delObject('portal_types')
        migrateLocalroleForm(self.portal, [])

    def testReorderUserActions(self):
        self.actions.user.moveObjectsToTop(['logout', 'undo', 'join'])
        reorderUserActions(self.portal, [])
        # build a dict that has the position as the value to make it easier to
        # compare postions in the ordered list of actions
        n = 0
        sort = {}
        for action in self.actions.user.objectIds():
            sort[action] = n
            n += 1
        self.failUnless(sort['preferences'] < sort['undo'])
        self.failUnless(sort['undo'] < sort['logout'])
        self.failUnless(sort['login'] < sort['join'])

    def testReorderUserActionsTwice(self):
        self.actions.user.moveObjectsToTop(['logout', 'undo', 'join'])
        reorderUserActions(self.portal, [])
        reorderUserActions(self.portal, [])
        # build a dict that has the position as the value to make it easier to
        # compare postions in the ordered list of actions
        n = 0
        sort = {}
        for action in self.actions.user.objectIds():
            sort[action] = n
            n += 1
        self.failUnless(sort['preferences'] < sort['undo'])
        self.failUnless(sort['undo'] < sort['logout'])
        self.failUnless(sort['login'] < sort['join'])

    def testReorderUserActionsNoTool(self):
        self.portal._delObject('portal_actions')
        reorderUserActions(self.portal, [])

    def testReorderUserActionsIncompleteActions(self):
        self.actions.user.moveObjectsToTop(['logout', 'undo', 'join'])
        self.actions.user._delObject('preferences')
        reorderUserActions(self.portal, [])
        # build a dict that has the position as the value to make it easier to
        # compare postions in the ordered list of actions
        n = 0
        sort = {}
        for action in self.actions.user.objectIds():
            sort[action] = n
            n += 1
        self.failUnless(sort['undo'] < sort['logout'])
        self.failUnless(sort['login'] < sort['join'])

    def testUpdateRtlCSSexpression(self):
        cssreg = self.portal.portal_css
        rtl = cssreg.getResource('RTL.css')
        rtl.setExpression('string:foo')
        updateRtlCSSexpression(self.portal, [])
        expr = rtl.getExpression()
        self.failUnless(expr == "python:portal.restrictedTraverse('@@plone_portal_state').is_rtl()")

    def testUpdateRtlCSSexpressionTwice(self):
        # perform migration twice
        cssreg = self.portal.portal_css
        rtl = cssreg.getResource('RTL.css')
        rtl.setExpression('string:foo')
        updateRtlCSSexpression(self.portal, [])
        updateRtlCSSexpression(self.portal, [])
        expr = rtl.getExpression()
        self.failUnless(expr == "python:portal.restrictedTraverse('@@plone_portal_state').is_rtl()")

    def testAddMaintenanceConfiglet(self):
        self.removeActionFromTool('Maintenance', action_provider='portal_controlpanel')
        addMaintenanceConfiglet(self.portal, [])
        self.failUnless('Maintenance' in [x.getId() for x in self.cp.listActions()])
        main = self.cp.getActionObject('Plone/Maintenance')
        self.assertEquals(main.title, 'Maintenance')
        self.assertEquals(main.action.text,
                          'string:${portal_url}/@@maintenance-controlpanel')

    def testAddMaintenanceConfigletTwice(self):
        self.removeActionFromTool('Maintenance', action_provider='portal_controlpanel')
        addMaintenanceConfiglet(self.portal, [])
        addMaintenanceConfiglet(self.portal, [])
        self.failUnless('Maintenance' in [x.getId() for x in self.cp.listActions()])
        main = self.cp.getActionObject('Plone/Maintenance')
        self.assertEquals(main.title, 'Maintenance')
        self.assertEquals(main.action.text,
                          'string:${portal_url}/@@maintenance-controlpanel')

    def testAddIconForMaintenanceConfiglet(self):
        # Should add the maintenance action icon
        self.removeActionIconFromTool('Maintenance')
        addIconForCalendarSettingsConfiglet(self.portal, [])
        self.failUnless('Maintenance' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForMaintenanceConfigletTwice(self):
        # Should add the maintenance action icon
        self.removeActionIconFromTool('Maintenance')
        addIconForCalendarSettingsConfiglet(self.portal, [])
        addIconForCalendarSettingsConfiglet(self.portal, [])
        self.failUnless('Maintenance' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddMaintenanceProperty(self):
        # adds a site property to portal_properties
        self.removeSiteProperty('number_of_days_to_keep')
        addMaintenanceProperty(self.portal, [])
        tool = self.portal.portal_properties
        sheet = tool.site_properties
        self.failUnless(sheet.hasProperty('number_of_days_to_keep'))
    
    def testAddLinkIntegritySwitch(self):
        # adds a site property to portal_properties
        self.removeSiteProperty('enable_link_integrity_checks')
        addLinkIntegritySwitch(self.portal, [])
        tool = self.portal.portal_properties
        sheet = tool.site_properties
        self.failUnless(sheet.hasProperty('enable_link_integrity_checks'))
    
    def testAddInlineEditingSwitch(self):
        # adds a site property to portal_properties
        self.removeSiteProperty('enable_inline_editing')
        loadMigrationProfile(self.portal,
                'profile-Products.CMFPlone.migrations:3.1.3-3.1.4',
                steps=["propertiestool"])
        tool = self.portal.portal_properties
        sheet = tool.site_properties
        self.failUnless(sheet.hasProperty('enable_inline_editing'))
    
    def testAddTableContents(self):
        css = self.portal.portal_css
        js = self.portal.portal_javascripts
        css.manage_removeStylesheet("toc.css")
        js.manage_removeScript("toc.js")
        addTableContents(self.portal, [])
        self.failUnless("toc.js" in js.getResourceIds())
        self.failUnless("toc.css" in css.getResourceIds())
        addTableContents(self.portal, [])
        self.failUnless("toc.js" in js.getResourceIds())
        self.failUnless("toc.css" in css.getResourceIds())
        
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


    def testPloneS5(self):
        pa = self.portal.portal_actions
        self.removeActionIconFromTool('s5_presentation')
        self.removeActionFromTool('s5_presentation', action_provider='portal_actions')
        installS5(self.portal, [])
        
        self.folder.invokeFactory('Document', id="test_document")
        doc_ids = self.portal.portal_actions.listFilteredActionsFor(self.folder.test_document)["document_actions"]
        assert "s5_presentation" not in [ i["id"] for i in doc_ids ]
        
        self.folder.invokeFactory('News Item', id="test_news_item")
        ni_ids = self.portal.portal_actions.listFilteredActionsFor(self.folder.test_news_item)["document_actions"]
        assert "s5_presentation" not in [ i["id"] for i in ni_ids ]
        
        # add in something to the document
        self.folder.test_document.setPresentation(True)
        self.folder.test_document.setText("<h1>Test</h1><p>foo</p>")
        
        # now it should appear
        doc_ids = self.portal.portal_actions.listFilteredActionsFor(self.folder.test_document)["document_actions"]
        assert "s5_presentation" in [ i["id"] for i in doc_ids ]
        
        # and install again
        self.failUnless('s5_presentation' in [x.getActionId() for x in self.icons.listActionIcons()])
        installS5(self.portal, [])
        self.failUnless('s5_presentation' in [x.getActionId() for x in self.icons.listActionIcons()])


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

    def testInstallContentrulesUtility(self):
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IRuleStorage)
        installContentRulesUtility(self.portal, [])
        installContentRulesUtility(self.portal, [])
        self.failIf(sm.queryUtility(IRuleStorage) is None)

    def testContentRulesConfiglet(self):
        pc = self.portal.portal_controlpanel
        self.removeActionIconFromTool('ContentRules')
        self.removeActionFromTool('ContentRules', action_provider='portal_controlpanel')
        addIconForContentRulesConfiglet(self.portal, [])
        addContentRulesConfiglet(self.portal, [])
        self.failUnless('ContentRules' in [x.getActionId() for x in self.icons.listActionIcons()])
        self.failUnless('ContentRules' in [x.getId() for x in pc.listActions()])


    def testUpdateSkinsAndSiteConfiglet(self):
        skins = self.cp.getActionObject('Plone/PortalSkin')
        site = self.cp.getActionObject('Plone/PloneReconfig')
        skins.action = Expression('string:skins')
        site.action = Expression('string:site')
        updateSkinsAndSiteConfiglet(self.portal, [])
        self.assertEquals(skins.title, 'Themes')
        self.assertEquals(skins.action.text,
                          'string:${portal_url}/@@skins-controlpanel')
        self.assertEquals(site.title, 'Site settings')
        self.assertEquals(site.action.text,
                          'string:${portal_url}/@@site-controlpanel')
    
    def testUpdateSkinsAndSiteConfigletTwice(self):
        # Should not fail if done twice
        skins = self.cp.getActionObject('Plone/PortalSkin')
        site = self.cp.getActionObject('Plone/PloneReconfig')
        skins.action = Expression('string:skins')
        site.action = Expression('string:site')
        updateSkinsAndSiteConfiglet(self.portal, [])
        updateSkinsAndSiteConfiglet(self.portal, [])
        self.assertEquals(skins.title, 'Themes')
        self.assertEquals(skins.action.text,
                          'string:${portal_url}/@@skins-controlpanel')
        self.assertEquals(site.title, 'Site settings')
        self.assertEquals(site.action.text,
                          'string:${portal_url}/@@site-controlpanel')

    def testUpdateSkinsAndSiteConfigletNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_controlpanel')
        updateSkinsAndSiteConfiglet(self.portal, [])

    def testUpdateConfigletTitles(self):
        collection = self.cp.getActionObject('Plone/portal_atct')
        language = self.cp.getActionObject('Plone/PloneLanguageTool')
        navigation = self.cp.getActionObject('Plone/NavigationSettings')
        types = self.cp.getActionObject('Plone/TypesSettings')
        users = self.cp.getActionObject('Plone/UsersGroups')
        users2 = self.cp.getActionObject('Plone/UsersGroups2')
        updateConfigletTitles(self.portal, [])
        self.assertEquals(collection.title, 'Collection')
        self.assertEquals(language.title, 'Language')
        self.assertEquals(navigation.title, 'Navigation')
        self.assertEquals(types.title, 'Types')
        self.assertEquals(users.title, 'Users and Groups')
        self.assertEquals(users2.title, 'Users and Groups')

    def testUpdateConfigletTitlesTwice(self):
        collection = self.cp.getActionObject('Plone/portal_atct')
        language = self.cp.getActionObject('Plone/PloneLanguageTool')
        navigation = self.cp.getActionObject('Plone/NavigationSettings')
        types = self.cp.getActionObject('Plone/TypesSettings')
        users = self.cp.getActionObject('Plone/UsersGroups')
        users2 = self.cp.getActionObject('Plone/UsersGroups2')
        updateConfigletTitles(self.portal, [])
        updateConfigletTitles(self.portal, [])
        self.assertEquals(collection.title, 'Collection')
        self.assertEquals(language.title, 'Language')
        self.assertEquals(navigation.title, 'Navigation')
        self.assertEquals(types.title, 'Types')
        self.assertEquals(users.title, 'Users and Groups')
        self.assertEquals(users2.title, 'Users and Groups')

    def testUpdateConfigletTitlesNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_controlpanel')
        updateConfigletTitles(self.portal, [])

    def testaddIconsForFilterAndSecurityConfigletsNoTool(self):
        # Should not fail if portal_actionicons is missing
        self.portal._delObject('portal_actionicons')
        addIconsForFilterAndSecurityConfiglets(self.portal, [])

    def testAddFilterAndSecurityConfiglets(self):
        self.removeActionFromTool('HtmlFilter', action_provider='portal_controlpanel')
        self.removeActionFromTool('SecuritySettings', action_provider='portal_controlpanel')
        addFilterAndSecurityConfiglets(self.portal, [])
        self.failUnless('HtmlFilter' in [x.getId() for x in self.cp.listActions()])
        self.failUnless('SecuritySettings' in [x.getId() for x in self.cp.listActions()])
        htmlfilter = self.cp.getActionObject('Plone/HtmlFilter')
        self.assertEquals(htmlfilter.title, 'HTML Filtering')
        self.assertEquals(htmlfilter.action.text,
                          'string:${portal_url}/@@filter-controlpanel')
        security = self.cp.getActionObject('Plone/SecuritySettings')
        self.assertEquals(security.title, 'Security')
        self.assertEquals(security.action.text,
                          'string:${portal_url}/@@security-controlpanel')

    def testAddFilterAndSecurityConfigletsTwice(self):
        # Should not fail if done twice
        self.removeActionFromTool('HtmlFilter', action_provider='portal_controlpanel')
        self.removeActionFromTool('SecuritySettings', action_provider='portal_controlpanel')
        addFilterAndSecurityConfiglets(self.portal, [])
        addFilterAndSecurityConfiglets(self.portal, [])
        self.failUnless('HtmlFilter' in [x.getId() for x in self.cp.listActions()])
        self.failUnless('SecuritySettings' in [x.getId() for x in self.cp.listActions()])
        htmlfilter = self.cp.getActionObject('Plone/HtmlFilter')
        self.assertEquals(htmlfilter.title, 'HTML Filtering')
        self.assertEquals(htmlfilter.action.text,
                          'string:${portal_url}/@@filter-controlpanel')
        security = self.cp.getActionObject('Plone/SecuritySettings')
        self.assertEquals(security.title, 'Security')
        self.assertEquals(security.action.text,
                          'string:${portal_url}/@@security-controlpanel')

    def testAddFilterAndSecurityConfigletsNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_controlpanel')
        addFilterAndSecurityConfiglets(self.portal, [])

    def testAddSitemapProperty(self):
        self.removeSiteProperty('enable_sitemap')
        addSitemapProperty(self.portal, [])
        tool = self.portal.portal_properties
        sheet = tool.site_properties
        self.failUnless(sheet.hasProperty('enable_sitemap'))

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
        # then migrate
        addCacheForResourceRegistry(self.portal, [])
        # and test
        self.failUnless(ram_cache_id in self.portal.objectIds())
        self.failUnless(cssreg.ZCacheable_enabled())
        self.failIf(cssreg.ZCacheable_getManagerId() is None)
        self.failUnless(jsreg.ZCacheable_enabled())
        self.failIf(jsreg.ZCacheable_getManagerId() is None)

    def testTablelessRemoval(self):
        st = getToolByName(self.portal, "portal_skins")
        if "Plone Tableless" not in st.getSkinSelections():
            st.addSkinSelection('Plone Tableless', 'one,two', make_default=True)
        removeTablelessSkin(self.portal, [])
        self.failIf('Plone Tableless' in st.getSkinSelections())
        self.failIf(st.default_skin == 'Plone Tableless')

    def testUpdateCssQueryJS(self):
        jsreg = self.portal.portal_javascripts
        jsreg.registerScript("folder_contents_hideAddItems.js")
        self.failUnless('folder_contents_hideAddItems.js' in jsreg.getResourceIds())
        # migrate and test again
        removeHideAddItemsJS(self.portal, [])
        self.failIf('folder_contents_hideAddItems.js' in jsreg.getResourceIds())
        # try double migration
        removeHideAddItemsJS(self.portal, [])

    def testAddWebstatsJSProperty(self):
        # adds a site property to portal_properties
        self.removeSiteProperty('webstats_js')
        addWebstatsJSProperty(self.portal, [])
        tool = self.portal.portal_properties
        sheet = tool.site_properties
        self.failUnless(sheet.hasProperty('webstats_js'))

    def testAddWebstatsJS(self):
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('webstats.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('webstats.js' in script_ids)
        # migrate and test again
        addWebstatsJSFile(self.portal, [])
        script_ids = jsreg.getResourceIds()
        self.failUnless('webstats.js' in script_ids)
        if 'webstats.js' in script_ids:
            pos1 = jsreg.getResourcePosition('toc.js')
            pos2 = jsreg.getResourcePosition('webstats.js')
            self.failUnless((pos2 - 1) == pos1)
        # check if enabled
        res = jsreg.getResource('webstats.js')
        self.assertEqual(res.getEnabled(),True)

    def testWebstatsJSTwice(self):
        # Should not break if migrated again
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('webstats.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('webstats.js' in script_ids)
        # migrate and test again
        addWebstatsJSFile(self.portal, [])
        addWebstatsJSFile(self.portal, [])
        script_ids = jsreg.getResourceIds()
        self.failUnless('webstats.js' in script_ids)
        if 'webstats.js' in script_ids:
            pos1 = jsreg.getResourcePosition('toc.js')
            pos2 = jsreg.getResourcePosition('webstats.js')
            self.failUnless((pos2 - 1) == pos1)
        # check if enabled 
        res = jsreg.getResource('webstats.js') 
        self.assertEqual(res.getEnabled(),True)

    def testaddIconsForFilterAndSecurityConfiglets(self):
        # Should add the filter and security action icons
        self.removeActionIconFromTool('HtmlFilter')
        self.removeActionIconFromTool('SecuritySettings')
        addIconsForFilterAndSecurityConfiglets(self.portal, [])
        self.failUnless('HtmlFilter' in [x.getActionId() for x in self.icons.listActionIcons()])
        self.failUnless('SecuritySettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testaddIconsForFilterAndSecurityConfigletsTwice(self):
        # Should not fail if migrated again
        self.removeActionIconFromTool('HtmlFilter')
        self.removeActionIconFromTool('SecuritySettings')
        addIconsForFilterAndSecurityConfiglets(self.portal, [])
        addIconsForFilterAndSecurityConfiglets(self.portal, [])
        self.failUnless('HtmlFilter' in [x.getActionId() for x in self.icons.listActionIcons()])
        self.failUnless('SecuritySettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testObjectProvidesIndex(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        if 'object_provides' in catalog.indexes():
            catalog.delIndex('object_provides')
        self.failIf('object_provides' in catalog.indexes())
        addObjectProvidesIndex(self.portal, [])
        self.failUnless('object_provides' in catalog.indexes())

    def testAddExternalLinksOpenNewWindowProperty(self):
        # adds a site property to portal_properties
        tool = self.portal.portal_properties
        sheet = tool.site_properties
        self.removeSiteProperty('external_links_open_new_window')
        addExternalLinksOpenNewWindowProperty(self.portal, [])
        self.failUnless(sheet.hasProperty('external_links_open_new_window'))
        self.failUnless(sheet.external_links_open_new_window == 'false')
        # Test migrations succeeds if run multiple times
        self.removeSiteProperty('external_links_open_new_window')
        addExternalLinksOpenNewWindowProperty(self.portal, [])
        addExternalLinksOpenNewWindowProperty(self.portal, [])
        self.failUnless(sheet.hasProperty('external_links_open_new_window'))
        self.failUnless(sheet.external_links_open_new_window == 'false')

    def testAddMissingWorkflowsNoTool(self):
        self.portal._delObject('portal_workflow')
        addMissingWorkflows(self.portal, [])

    def testAddManyGroupsProperty(self):
        # adds a site property to portal_properties
        tool = self.portal.portal_properties
        sheet = tool.site_properties
        self.removeSiteProperty('many_groups')
        addManyGroupsProperty(self.portal, [])
        self.failUnless(sheet.hasProperty('many_groups'))
        self.failUnless(sheet.many_groups == False)
        # Test migrations succeeds if run multiple times
        self.removeSiteProperty('many_groups')
        addManyGroupsProperty(self.portal, [])
        addManyGroupsProperty(self.portal, [])
        self.failUnless(sheet.hasProperty('many_groups'))
        self.failUnless(sheet.many_groups == False)

    def testMigratePloneTool(self):
        from Products.CMFPlone import ToolNames
        tool = self.portal.plone_utils
        tool.meta_type = 'PlonePAS Utilities Tool'
        restorePloneTool(self.portal, [])
        tool = self.portal.plone_utils
        self.assertEquals(ToolNames.UtilsTool, tool.meta_type)

    def testInstallI18NUtilities(self):
        sm = getSiteManager()
        sm.unregisterUtility(provided=ICountries)
        sm.unregisterUtility(provided=IContentLanguages)
        sm.unregisterUtility(provided=IMetadataLanguages)
        installI18NUtilities(self.portal, [])
        self.failIf(sm.queryUtility(ICountries) is None)
        self.failIf(sm.queryUtility(IContentLanguages) is None)
        self.failIf(sm.queryUtility(IMetadataLanguages) is None)

    def testInstallI18NUtilitiesTwice(self):
        sm = getSiteManager()
        sm.unregisterUtility(provided=ICountries)
        sm.unregisterUtility(provided=IContentLanguages)
        sm.unregisterUtility(provided=IMetadataLanguages)
        installI18NUtilities(self.portal, [])
        installI18NUtilities(self.portal, [])
        self.failIf(sm.queryUtility(ICountries) is None)
        self.failIf(sm.queryUtility(IContentLanguages) is None)
        self.failIf(sm.queryUtility(IMetadataLanguages) is None)

    def testInstallPloneLanguageTool(self):
        CMFSite.manage_delObjects(self.portal, ['portal_languages'])
        self.uninstallProduct('PloneLanguageTool')
        qi = getToolByName(self.portal, "portal_quickinstaller")
        installProduct('PloneLanguageTool', self.portal, [])
        self.failUnless(qi.isProductInstalled('PloneLanguageTool'))
        self.failUnless('portal_languages' in self.portal.keys())

    def testAddEmailCharsetProperty(self):
        if self.portal.hasProperty('email_charset'):
            self.portal.manage_delProperties(['email_charset'])
        addEmailCharsetProperty(self.portal, [])
        self.failUnless(self.portal.hasProperty('email_charset'))
        self.assertEquals(self.portal.getProperty('email_charset'), 'utf-8')

    def testAddEmailCharsetPropertyTwice(self):
        out = []
        if self.portal.hasProperty('email_charset'):
            self.portal.manage_delProperties(['email_charset'])
        addEmailCharsetProperty(self.portal, out)
        addEmailCharsetProperty(self.portal, out)
        self.failUnless(self.portal.hasProperty('email_charset'))
        self.assertEquals(self.portal.getProperty('email_charset'), 'utf-8')

    def testChangeOrderOfActionProviders(self):
        out = []
        self.actions.deleteActionProvider('portal_types')
        self.actions.addActionProvider('portal_types')
        self.assertEquals(
            self.actions.listActionProviders(),
            ('portal_workflow', 'portal_actions', 'portal_types'))
        changeOrderOfActionProviders(self.portal, out)
        self.assertEquals(
            self.actions.listActionProviders(),
            ('portal_workflow', 'portal_types', 'portal_actions'))

    def testChangeOrderOfActionProvidersTwice(self):
        out = []
        self.actions.deleteActionProvider('portal_types')
        self.actions.addActionProvider('portal_types')
        self.assertEquals(
            self.actions.listActionProviders(),
            ('portal_workflow', 'portal_actions', 'portal_types'))
        changeOrderOfActionProviders(self.portal, out)
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

        cleanupOldActions(self.portal, out)

        self.failIf('reply' in object_.keys())
        self.failIf('logged_in' in user.keys())
        self.failIf('object_tabs' in self.actions.keys())
        self.failIf('global' in self.actions.keys())

    def testCleanupOldActionsTwice(self):
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

        cleanupOldActions(self.portal, out)
        cleanupOldActions(self.portal, out)

        self.failIf('reply' in object_.keys())
        self.failIf('logged_in' in user.keys())
        self.failIf('object_tabs' in self.actions.keys())
        self.failIf('global' in self.actions.keys())

    def testCharsetCleanup(self):
        if not self.portal.hasProperty('default_charset'):
            self.portal.manage_addProperty('default_charset', '', 'string')

        self.portal.manage_changeProperties(default_charset = 'latin1')
        cleanDefaultCharset(self.portal, [])
        self.assertEqual(self.portal.getProperty('default_charset', 'nothere'),
                'latin1')

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

        action_ids = [x.getId() for x in document.listActions()]
        assert "s5_presentation" not in action_ids

        icon_ids = [x.getActionId() for x in ait.listActionIcons()]
        assert "s5_presentation" not in icon_ids

        installS5(self.portal, [])

        action_ids = [x.getId() for x in document.listActions()]
        assert "s5_presentation" in action_ids

        icon_ids = [x.getActionId() for x in ait.listActionIcons()]
        assert "s5_presentation" in icon_ids

        removeS5Actions(self.portal, [])

        action_ids = [x.getId() for x in document.listActions()]
        assert "s5_presentation" not in action_ids

        icon_ids = [x.getActionId() for x in ait.listActionIcons()]
        assert "s5_presentation" not in icon_ids

    def testAddCacheForKSSRegistry(self):
        ram_cache_id = 'ResourceRegistryCache'
        kssreg = self.portal.portal_kss
        kssreg.ZCacheable_setEnabled(0)
        kssreg.ZCacheable_setManagerId(None)
        self.failIf(kssreg.ZCacheable_enabled())
        self.failUnless(kssreg.ZCacheable_getManagerId() is None)
        # migrate
        addCacheForKSSRegistry(self.portal, [])
        # and test
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
        addContributorToCreationPermissions(self.portal, [])
        roles = sorted([r['name'] for r in self.portal.rolesOfPermission('Add portal content') if r['selected']])
        self.assertEquals(['Contributor', 'Manager'], roles)
        self.assertEquals(False, bool(self.portal.acquiredRolesAreUsedBy('Add portal content')))
                                
    def testAddEditorToCreationPermissionsTwice(self):
        self.portal._delRoles(['Contributor',])
        for p in ['Add portal content', 'Add portal folders', 'ATContentTypes: Add Document',
                    'ATContentTypes: Add Event', 'ATContentTypes: Add Favorite',
                    'ATContentTypes: Add File', 'ATContentTypes: Add Folder', 
                    'ATContentTypes: Add Image', 'ATContentTypes: Add Large Plone Folder',
                    'ATContentTypes: Add Link', 'ATContentTypes: Add News Item', ]:
            self.portal.manage_permission(p, ['Manager', 'Owner'], True)
        addContributorToCreationPermissions(self.portal, [])
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
        # perform migration twice
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
        removeSharingAction(self.portal, [])
        self.failIf('local_roles' in [a.id for a in fti.listActions()])
        
    def testRemoveSharingActionNoTool(self):
        self.portal._delOb('portal_types')
        removeSharingAction(self.portal, [])
        
    def testRemoveSharingActionTwice(self):
        fti = self.types['Document']
        fti.addAction(id='local_roles', name='Sharing', 
                      action='string:${object_url}/sharing',
                      condition=None, permission='Manage properties',
                      category='object')
        removeSharingAction(self.portal, [])
        removeSharingAction(self.portal, [])
        self.failIf('local_roles' in [a.id for a in fti.listActions()])
        
    def testAddContributorToCreationPermissions(self):
        for p in ['Manage properties', 'Modify view template', 'Request review']:
            self.portal.manage_permission(p, ['Manager', 'Owner'], True)
        addEditorToSecondaryEditorPermissions(self.portal, [])
        for p in ['Manage properties', 'Modify view template', 'Request review']:
            self.failUnless(p in [r['name'] for r in 
                self.portal.permissionsOfRole('Editor') if r['selected']])

    def testAddEditorToCreationPermissionsNoStomp(self):
        self.portal.manage_permission('Manage properties', ['Manager'], False)
        addEditorToSecondaryEditorPermissions(self.portal, [])
        roles = sorted([r['name'] for r in self.portal.rolesOfPermission('Manage properties') if r['selected']])
        self.assertEquals(['Editor', 'Manager'], roles)
        self.assertEquals(False, bool(self.portal.acquiredRolesAreUsedBy('Manage properties')))
                                
    def testAddEditorToSecondaryEditPermissionsTwice(self):
        for p in ['Manage properties', 'Modify view template', 'Request review']:
            self.portal.manage_permission(p, ['Manager', 'Owner'], True)
        addEditorToSecondaryEditorPermissions(self.portal, [])
        addEditorToSecondaryEditorPermissions(self.portal, [])
        for p in ['Manage properties', 'Modify view template', 'Request review']:
            self.failUnless(p in [r['name'] for r in 
                self.portal.permissionsOfRole('Editor') if r['selected']])

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
        updateEditActionConditionForLocking(self.portal, out)
        for contentType in lockable_types:
            fti = self.types.getTypeInfo(contentType)
            for action in fti.listActions():
                if action.getId() == 'edit':
                    expressionCondition = action.condition
                    self.assertEquals(action.condition.text, "not:object/@@plone_lock_info/is_locked_for_current_user|python:True")

    def testUpdateEditActionConditionForLockingTwice(self):
        out = []
        lockable_types = ['Document', 'Event', 'Favorite', 'File', 'Folder',
                          'Image', 'Large Plone Folder', 'Link',
                          'News Item', 'Topic']
        for contentType in lockable_types:
            fti = self.types.getTypeInfo(contentType)
            for action in fti.listActions():
                if action.getId() == 'edit':
                    action.condition = ''
        updateEditActionConditionForLocking(self.portal, out)
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
        # migrate and test again
        addOnFormUnloadJS(self.portal, [])
        script_ids = jsreg.getResourceIds()
        self.failUnless('unlockOnFormUnload.js' in script_ids)

    def testAddOnFormUnloadRegistrationJSTwice(self):
        jsreg = self.portal.portal_javascripts
        # unregister first
        jsreg.unregisterResource('unlockOnFormUnload.js')
        script_ids = jsreg.getResourceIds()
        self.failIf('unlockOnFormUnload.js' in script_ids)
        # migrate and test again
        addOnFormUnloadJS(self.portal, [])
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
        # migrate
        moveKupuAndCMFPWControlPanel(self.portal, [])
        kupu = self.cp.getActionObject('Plone/kupu')
        self.assertEquals(kupu.getCategory(), 'Plone')
        cmfpw = self.cp.getActionObject('Products/placefulworkflow')
        self.assertEquals(cmfpw.getCategory(), 'Products')

    def testMoveKupuAndCMFPWControlPanelTwice(self):
        # Should not fail if done twice
        kupu = self.cp.getActionObject('Plone/kupu')
        kupu.category = 'Products'
        cmfpw = self.cp.getActionObject('Products/placefulworkflow')
        if cmfpw is None:
            self.cp.registerConfiglet(**placeful_prefs_configlet)
        cmfpw = self.cp.getActionObject('Products/placefulworkflow')
        cmfpw.category = 'Plone'
        # migrate
        moveKupuAndCMFPWControlPanel(self.portal, [])
        moveKupuAndCMFPWControlPanel(self.portal, [])
        kupu = self.cp.getActionObject('Plone/kupu')
        self.assertEquals(kupu.getCategory(), 'Plone')
        cmfpw = self.cp.getActionObject('Products/placefulworkflow')
        self.assertEquals(cmfpw.getCategory(), 'Products')

    def testMoveKupuAndCMFPWControlPanelNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_controlpanel')
        moveKupuAndCMFPWControlPanel(self.portal, [])

    def testUpdateLanguageControlPanel(self):
        lang = self.cp.getActionObject('Plone/PloneLanguageTool')
        lang.action = Expression('string:lang')
        updateLanguageControlPanel(self.portal, [])
        self.assertEquals(lang.action.text,
                          'string:${portal_url}/@@language-controlpanel')

    def testUpdateLanguageControlPanelTwice(self):
        # Should not fail if done twice
        lang = self.cp.getActionObject('Plone/PloneLanguageTool')
        lang.action = Expression('string:lang')
        updateLanguageControlPanel(self.portal, [])
        updateLanguageControlPanel(self.portal, [])
        self.assertEquals(lang.action.text,
                          'string:${portal_url}/@@language-controlpanel')

    def testUpdateLanguageControlPanelNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_controlpanel')
        updateLanguageControlPanel(self.portal, [])

    def testUpdateTopicTitle(self):
        topic = self.types.get('Topic')
        topic.title = 'Unmigrated'
        updateTopicTitle(self.portal, [])
        self.failUnless(topic.title == 'Collection')

    def testUpdateTopicTitleTwice(self):
        topic = self.types.get('Topic')
        topic.title = 'Unmigrated'
        updateTopicTitle(self.portal, [])
        updateTopicTitle(self.portal, [])
        self.failUnless(topic.title == 'Collection')

    def testUpdateTopicTitleNoTool(self):
        self.portal._delObject('portal_types')
        updateTopicTitle(self.portal, [])

    def testAddIntelligentText(self):
        # Before migration, the mime type and transforms of
        # intelligent text are not available.  They *are* here in a
        # fresh site, so we may need to remove them first for testing.

        # First we remove the transforms, as they depend on the
        # mimetype being there.
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

        out = []
        addIntelligentText(self.portal, out)
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

class TestMigrations_v3_1(MigrationTest):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller
        self.wf = self.portal.portal_workflow
        self.ps = self.portal.portal_setup

    def testReinstallCMFPlacefulWorkflow(self):
        # first the product needs to be installed
        self.qi.installProduct('CMFPlacefulWorkflow')
        # Delete existing logs to prevent race condition
        self.ps.manage_delObjects(self.ps.objectIds())
        # We remove the new marker, to ensure it's added on reinstall
        if IPlacefulMarker.providedBy(self.wf):
            noLongerProvides(self.wf, IPlacefulMarker)
        reinstallCMFPlacefulWorkflow(self.portal, [])
        self.failUnless(IPlacefulMarker.providedBy(self.wf))

    def testReinstallCMFPlacefulWorkflowDoesNotInstall(self):
        reinstallCMFPlacefulWorkflow(self.portal, [])
        self.failIf(self.qi.isProductInstalled('CMFPlacefulWorkflow'))

    def testReinstallCMFPlacefulWorkflowNoTool(self):
        self.portal._delObject('portal_quickinstaller')
        reinstallCMFPlacefulWorkflow(self.portal, [])

    def testReplaceLocalRoleManager(self):
        # first we replace the local role manager with the one from PlonePAS
        uf = self.portal.acl_users
        # deactivate and remove the borg plugin
        uf.plugins.removePluginById('borg_localroles')
        uf.manage_delObjects(['borg_localroles'])
        # activate the standard plugin
        uf.plugins.activatePlugin(ILocalRolesPlugin, 'local_roles')
        # Bring things back to normal
        replace_local_role_manager(self.portal, [])
        plugins = uf.plugins.listPlugins(ILocalRolesPlugin)
        self.failUnlessEqual(len(plugins), 1)
        self.failUnlessEqual(plugins[0][0], 'borg_localroles')

    def testReplaceLocalRoleManagerTwice(self):
        # first we replace the local role manager with the one from PlonePAS
        uf = self.portal.acl_users
        # deactivate and remove the borg plugin
        uf.plugins.removePluginById('borg_localroles')
        uf.manage_delObjects(['borg_localroles'])
        # activate the standard plugin
        uf.plugins.activatePlugin(ILocalRolesPlugin, 'local_roles')
        # run the migration twice
        replace_local_role_manager(self.portal, [])
        replace_local_role_manager(self.portal, [])
        plugins = uf.plugins.listPlugins(ILocalRolesPlugin)
        self.failUnlessEqual(len(plugins), 1)
        self.failUnlessEqual(plugins[0][0], 'borg_localroles')

    def testReplaceLocalRoleManagerNoPlugin(self):
        # first we replace the local role manager with the one from PlonePAS
        uf = self.portal.acl_users
        # deactivate and remove the borg plugin
        uf.plugins.removePluginById('borg_localroles')
        uf.manage_delObjects(['borg_localroles'])
        # delete the standard plugin
        uf.manage_delObjects(['local_roles'])
        # Run the migration, which shouldn't fail even if the expected
        # plugin is missing
        replace_local_role_manager(self.portal, [])
        plugins = uf.plugins.listPlugins(ILocalRolesPlugin)
        self.failUnlessEqual(len(plugins), 1)
        self.failUnlessEqual(plugins[0][0], 'borg_localroles')

    def testReplaceLocalRoleManagerNoPAS(self):
        uf = self.portal.acl_users
        # delete the plugin registry
        uf._delObject('plugins')
        replace_local_role_manager(self.portal, [])

    def testReplaceLocalRoleManagerNoUF(self):
        # Delete the user folder
        uf = self.portal._delObject('acl_users')
        replace_local_role_manager(self.portal, [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v2_1_1))
    suite.addTest(makeSuite(TestMigrations_v2_1_2))
    suite.addTest(makeSuite(TestMigrations_v2_1_3))
    suite.addTest(makeSuite(TestMigrations_v2_5))
    suite.addTest(makeSuite(TestMigrations_v2_5_1))
    suite.addTest(makeSuite(TestMigrations_v2_5_2))
    suite.addTest(makeSuite(TestMigrations_v2_5_4))
    suite.addTest(makeSuite(TestMigrations_v3_0))
    suite.addTest(makeSuite(TestMigrations_v3_0_Actions))
    suite.addTest(makeSuite(TestMigrations_v3_1))
    return suite
