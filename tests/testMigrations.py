#
# Tests for migration components
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from sets import Set
from Products.CMFPlone.tests import PloneTestCase

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.Expression import Expression
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFPlone.PloneTool import AllowSendto
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer

from Products.CMFPlone.migrations.v2.two04_two05 import replaceFolderPropertiesWithEdit
from Products.CMFPlone.migrations.v2.two04_two05 import interchangeEditAndSharing
from Products.CMFPlone.migrations.v2.two04_two05 import addFolderListingActionToTopic

from Products.CMFPlone.migrations.v2_1.alphas import addFullScreenAction
from Products.CMFPlone.migrations.v2_1.alphas import addFullScreenActionIcon
from Products.CMFPlone.migrations.v2_1.alphas import addVisibleIdsSiteProperty
from Products.CMFPlone.migrations.v2_1.alphas import deleteVisibleIdsMemberProperty
from Products.CMFPlone.migrations.v2_1.alphas import deleteFormToolTipsMemberProperty
from Products.CMFPlone.migrations.v2_1.alphas import switchPathIndex
from Products.CMFPlone.migrations.v2_1.alphas import addGetObjPositionInParentIndex
from Products.CMFPlone.migrations.v2_1.alphas import addGetObjSizeMetadata
from Products.CMFPlone.migrations.v2_1.alphas import updateNavTreeProperties
from Products.CMFPlone.migrations.v2_1.alphas import addSitemapAction
from Products.CMFPlone.migrations.v2_1.alphas import addDefaultGroups
from Products.CMFPlone.migrations.v2_1.alphas import reindexCatalog
from Products.CMFPlone.migrations.v2_1.alphas import installCSSandJSRegistries
from Products.CMFPlone.migrations.v2_1.alphas import addUnfriendlyTypesSiteProperty
from Products.CMFPlone.migrations.v2_1.alphas import addNonDefaultPageTypesSiteProperty
from Products.CMFPlone.migrations.v2_1.alphas import removePortalTabsActions
from Products.CMFPlone.migrations.v2_1.alphas import addNewsFolder
from Products.CMFPlone.migrations.v2_1.alphas import addEventsFolder
from Products.CMFPlone.migrations.v2_1.alphas import addExclude_from_navMetadata
from Products.CMFPlone.migrations.v2_1.alphas import addIs_FolderishMetadata
from Products.CMFPlone.migrations.v2_1.alphas import indexMembersFolder
from Products.CMFPlone.migrations.v2_1.alphas import addEditContentActions
from Products.CMFPlone.migrations.v2_1.alphas import migrateDateIndexes
from Products.CMFPlone.migrations.v2_1.alphas import migrateDateRangeIndexes
from Products.CMFPlone.migrations.v2_1.alphas import addSortable_TitleIndex
from Products.CMFPlone.migrations.v2_1.alphas import addDefaultTypesToPortalFactory
from Products.CMFPlone.migrations.v2_1.alphas import addNewsTopic
from Products.CMFPlone.migrations.v2_1.alphas import addEventsTopic
from Products.CMFPlone.migrations.v2_1.alphas import addDisableFolderSectionsSiteProperty
from Products.CMFPlone.migrations.v2_1.alphas import addSiteRootViewTemplates
from Products.CMFPlone.migrations.v2_1.alphas import addMemberdataHome_Page
from Products.CMFPlone.migrations.v2_1.alphas import addMemberdataLocation
from Products.CMFPlone.migrations.v2_1.alphas import addMemberdataLanguage
from Products.CMFPlone.migrations.v2_1.alphas import addMemberdataDescription
from Products.CMFPlone.migrations.v2_1.alphas import addMemberdataExtEditor
from Products.CMFPlone.migrations.v2_1.alphas import alterChangeStateActionCondition
from Products.CMFPlone.migrations.v2_1.alphas import alterExtEditorActionCondition
from Products.CMFPlone.migrations.v2_1.alphas import fixFolderButtonsActions
from Products.CMFPlone.migrations.v2_1.alphas import addTypesUseViewActionInListingsProperty
from Products.CMFPlone.migrations.v2_1.alphas import switchToExpirationDateMetadata
from Products.CMFPlone.migrations.v2_1.alphas import changePloneSetupActionToSiteSetup
from Products.CMFPlone.migrations.v2_1.alphas import changePloneSiteIcon
from Products.CMFPlone.migrations.v2_1.alphas import convertPloneFTIToCMFDynamicViewFTI
from Products.CMFPlone.migrations.v2_1.alphas import replaceMailHost

from Products.CMFPlone.migrations.v2_1.betas import fixObjectPasteActionForDefaultPages
from Products.CMFPlone.migrations.v2_1.betas import fixBatchActionToggle
from Products.CMFPlone.migrations.v2_1.betas import fixMyFolderAction
from Products.CMFPlone.migrations.v2_1.betas import reorderStylesheets
from Products.CMFPlone.migrations.v2_1.betas import allowOwnerToAccessInactiveContent
from Products.CMFPlone.migrations.v2_1.betas import restrictNewsTopicToPublished
from Products.CMFPlone.migrations.v2_1.betas import restrictEventsTopicToPublished
from Products.CMFPlone.migrations.v2_1.betas import addCssQueryJS
from Products.CMFPlone.migrations.v2_1.betas import exchangePloneMenuWithDropDown
from Products.CMFPlone.migrations.v2_1.betas import removePlonePrefixFromStylesheets
from Products.CMFPlone.migrations.v2_1.betas import add3rdPartySkinPath
from Products.CMFPlone.migrations.v2_1.betas import addEnableLivesearchProperty
from Products.CMFPlone.migrations.v2_1.betas import addIconForSearchSettingsConfiglet
from Products.CMFPlone.migrations.v2_1.betas import sanitizeCookieCrumbler
from Products.CMFPlone.migrations.v2_1.betas import convertNavTreeWhitelistToBlacklist
from Products.CMFPlone.migrations.v2_1.betas import addIsDefaultPageIndex
from Products.CMFPlone.migrations.v2_1.betas import addIsFolderishIndex
from Products.CMFPlone.migrations.v2_1.betas import fixContentActionConditions
from Products.CMFPlone.migrations.v2_1.betas import fixFolderlistingAction
from Products.CMFPlone.migrations.v2_1.betas import fixFolderContentsActionAgain
from Products.CMFPlone.migrations.v2_1.betas import changePortalActionCategory
from Products.CMFPlone.migrations.v2_1.betas import addMethodAliasesForPloneSite
from Products.CMFPlone.migrations.v2_1.betas import updateParentMetaTypesNotToQuery
from Products.CMFPlone.migrations.v2_1.betas import fixCutActionPermission
from Products.CMFPlone.migrations.v2_1.betas import fixExtEditAction
from Products.CMFPlone.migrations.v2_1.betas import changeMemberdataExtEditor
from Products.CMFPlone.migrations.v2_1.betas import fixWorkflowStateTitles
from Products.CMFPlone.migrations.v2_1.betas import changeSiteActions
from Products.CMFPlone.migrations.v2_1.betas import removePloneSetupActionFromPortalMembership
from Products.CMFPlone.migrations.v2_1.betas import fixViewMethodAliases
from Products.CMFPlone.migrations.v2_1.betas import fixPortalEditAndSharingActions
from Products.CMFPlone.migrations.v2_1.betas import addCMFUidTools
from Products.CMFPlone.migrations.v2_1.betas import fixCSSMediaTypes
from Products.CMFPlone.migrations.v2_1.betas import addWFStateFilteringToNavTree
from Products.CMFPlone.migrations.v2_1.betas import addIconForNavigationSettingsConfiglet
from Products.CMFPlone.migrations.v2_1.betas import addSearchAndNavigationConfiglets
from Products.CMFPlone.migrations.v2_1.betas import setupAllowSendtoPermission
from Products.CMFPlone.migrations.v2_1.betas import readdVisibleIdsMemberProperty
from Products.CMFPlone.migrations.v2_1.betas import addCMFTypesToSearchBlackList
from Products.CMFPlone.migrations.v2_1.betas import convertDefaultPageTypesToWhitelist

from Products.CMFPlone.migrations.v2_1.rcs import changeAvailableViewsForFolders
from Products.CMFPlone.migrations.v2_1.rcs import enableSyndicationOnTopics
from Products.CMFPlone.migrations.v2_1.rcs import disableSyndicationAction
from Products.CMFPlone.migrations.v2_1.rcs import alterRSSActionTitle
from Products.CMFPlone.migrations.v2_1.rcs import addPastEventsTopic
from Products.CMFPlone.migrations.v2_1.rcs import addDateCriterionToEventsTopic
from Products.CMFPlone.migrations.v2_1.rcs import fixDuplicatePortalRootSharingAction
from Products.CMFPlone.migrations.v2_1.rcs import moveDefaultTopicsToPortalRoot
from Products.CMFPlone.migrations.v2_1.rcs import alterSortCriterionOnNewsTopic
from Products.CMFPlone.migrations.v2_1.rcs import fixPreferenceActionTitle
from Products.CMFPlone.migrations.v2_1.rcs import changeNewsTopicDefaultView
from Products.CMFPlone.migrations.v2_1.rcs import fixCMFLegacyLayer
from Products.CMFPlone.migrations.v2_1.rcs import reorderObjectButtons
from Products.CMFPlone.migrations.v2_1.rcs import allowMembersToViewGroups
from Products.CMFPlone.migrations.v2_1.rcs import reorderStylesheets as reorderStylesheets_rc3_final

from Products.CMFPlone.migrations.v2_1.final_two11 import reindexPathIndex
from Products.CMFPlone.migrations.v2_1.two11_two12 import removeCMFTopicSkinLayer
from Products.CMFPlone.migrations.v2_1.two11_two12 import addRenameObjectButton
from Products.CMFPlone.migrations.v2_1.two11_two12 import addSEHighLightJS
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

from Products.CMFDynamicViewFTI.migrate import migrateFTI

import types

class BogusMailHost(SimpleItem):
    meta_type = 'Bad Mailer'
    title = 'Mailer'
    smtp_port = 37
    smtp_host = 'my.badhost.com'


class MigrationTest(PloneTestCase.PloneTestCase):

    def removeActionFromType(self, type_name, action_id):
        # Removes an action from a portal type
        tool = getattr(self.portal, 'portal_types')
        info = tool.getTypeInfo(type_name)
        typeob = getattr(tool, info.getId())
        actions = info.listActions()
        actions = [x for x in actions if x.id != action_id]
        typeob._actions = tuple(actions)

    def addActionToType(self, type_name, action_id, category):
        # Adds an action to a portal type
        tool = getattr(self.portal, 'portal_types')
        info = tool.getTypeInfo(type_name)
        typeob = getattr(tool, info.getId())
        typeob.addAction(action_id, action_id, '', '', '', category)

    def removeActionFromTool(self, action_id, category=None, action_provider='portal_actions'):
        # Removes an action from portal_actions
        tool = getattr(self.portal, action_provider)
        actions = tool.listActions()
        actions = [x for x in actions if not (x.id == action_id and
                   (category is None or x.category == category))]
        tool._actions = tuple(actions)

    def addActionToTool(self, action_id, category, action_provider='portal_actions'):
        # Adds an action to portal_actions
        tool = getattr(self.portal, action_provider)
        tool.addAction(action_id, action_id, '', '', '', category)

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


class TestMigrations_v2(MigrationTest):

    def afterSetUp(self):
        self.types = self.portal.portal_types

    def testReplaceFolderPropertiesWithEditNoFolder(self):
        # Should not fail if Folder type is missing
        self.types._delObject('Folder')
        replaceFolderPropertiesWithEdit(self.portal, [])

    def testReplaceFolderPropertiesWithEditNoEdit(self):
        # Should not fail if action is missing
        self.removeActionFromType('Folder', 'edit')
        replaceFolderPropertiesWithEdit(self.portal, [])

    def testInterchangeEditAndSharingNoFolder(self):
        # Should not fail if Folder type is missing
        self.types._delObject('Folder')
        interchangeEditAndSharing(self.portal, [])

    def testInterchangeEditAndSharingNoSharing(self):
        # Should not fail if action is missing
        self.removeActionFromType('Folder', 'local_roles')
        interchangeEditAndSharing(self.portal, [])

    def testInterchangeEditAndSharingNoEdit(self):
        # Should not fail if action is missing
        self.removeActionFromType('Folder', 'edit')
        interchangeEditAndSharing(self.portal, [])

    def testAddFolderListingToTopicNoTopic(self):
        # Should not fail if Topic type is missing
        self.types._delObject('Topic')
        addFolderListingActionToTopic(self.portal, [])


class TestMigrations_v2_1(MigrationTest):

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
#       self.cc = self.portal.cookie_authentication
        self.cp = self.portal.portal_controlpanel
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types

    def testAddFullScreenAction(self):
        # Should add the full_screen action
        self.removeActionFromTool('full_screen')
        addFullScreenAction(self.portal, [])
        self.failUnless('full_screen' in [x.id for x in self.actions.listActions()])

    def testAddFullScreenActionTwice(self):
        # Should not fail if migrated again
        self.removeActionFromTool('full_screen')
        addFullScreenAction(self.portal, [])
        addFullScreenAction(self.portal, [])
        self.failUnless('full_screen' in [x.id for x in self.actions.listActions()])

    def testAddFullScreenActionNoTool(self):
        # Should not fail if portal_actions is missing
        self.portal._delObject('portal_actions')
        addFullScreenAction(self.portal, [])

    def testAddFullScreenActionIcon(self):
        # Should add the full_screen action icon
        self.removeActionIconFromTool('full_screen')
        addFullScreenActionIcon(self.portal, [])
        self.failUnless('full_screen' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddFullScreenActionIconTwice(self):
        # Should not fail if migrated again
        self.removeActionIconFromTool('full_screen')
        addFullScreenActionIcon(self.portal, [])
        addFullScreenActionIcon(self.portal, [])
        self.failUnless('full_screen' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddFullScreenActionIconNoTool(self):
        # Should not fail if portal_actionicons is missing
        self.portal._delObject('portal_actionicons')
        addFullScreenActionIcon(self.portal, [])

    def testAddVisibleIdsSiteProperty(self):
        # Should add the visible_ids property
        self.removeSiteProperty('visible_ids')
        self.failIf(self.properties.site_properties.hasProperty('visible_ids'))
        addVisibleIdsSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('visible_ids'))

    def testAddVisibleIdsSitePropertyTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('visible_ids')
        self.failIf(self.properties.site_properties.hasProperty('visible_ids'))
        addVisibleIdsSiteProperty(self.portal, [])
        addVisibleIdsSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('visible_ids'))

    def testAddVisibleIdsSitePropertyNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addVisibleIdsSiteProperty(self.portal, [])

    def testAddVisibleIdsSitePropertyNoSheet(self):
        # Should not fail if site_properties is missing
        self.properties._delObject('site_properties')
        addVisibleIdsSiteProperty(self.portal, [])

    def testDeleteVisibleIdsMemberProperty(self):
        # Should delete the memberdata property
        if not self.memberdata.hasProperty('visible_ids'):
            self.memberdata.manage_addProperty('visible_ids', 0, 'boolean')
        self.failUnless(self.memberdata.hasProperty('visible_ids'))
        deleteVisibleIdsMemberProperty(self.portal, [])
        self.failIf(self.memberdata.hasProperty('visible_ids'))

    def testDeleteVisibleIdsMemberPropertyTwice(self):
        # Should not fail if migrated again
        if not self.memberdata.hasProperty('visible_ids'):
            self.memberdata.manage_addProperty('visible_ids', 0, 'boolean')
        self.failUnless(self.memberdata.hasProperty('visible_ids'))
        deleteVisibleIdsMemberProperty(self.portal, [])
        deleteVisibleIdsMemberProperty(self.portal, [])
        self.failIf(self.memberdata.hasProperty('visible_ids'))

    def testDeleteVisibleIdsMemberPropertyNoTool(self):
        # Should not fail if portal_memberdata is missing
        self.portal._delObject('portal_memberdata')
        deleteVisibleIdsMemberProperty(self.portal, [])

    def testDeleteFormToolTipsMemberProperty(self):
        # Should delete the memberdata property
        if not self.memberdata.hasProperty('formtooltips'):
            self.memberdata.manage_addProperty('formtooltips', 0, 'boolean')
        self.failUnless(self.memberdata.hasProperty('formtooltips'))
        deleteFormToolTipsMemberProperty(self.portal, [])
        self.failIf(self.memberdata.hasProperty('formtooltips'))

    def testDeleteFormToolTipsMemberPropertyTwice(self):
        # Should not fail if migrated again
        if not self.memberdata.hasProperty('formtooltips'):
            self.memberdata.manage_addProperty('formtooltips', 0, 'boolean')
        self.failUnless(self.memberdata.hasProperty('formtooltips'))
        deleteFormToolTipsMemberProperty(self.portal, [])
        deleteFormToolTipsMemberProperty(self.portal, [])
        self.failIf(self.memberdata.hasProperty('formtooltips'))

    def testDeleteFormToolTipsMemberPropertyNoTool(self):
        # Should not fail if portal_memberdata is missing
        self.portal._delObject('portal_memberdata')
        deleteFormToolTipsMemberProperty(self.portal, [])

    def testSwitchPathIndex(self):
        # Should convert 'path' index to EPI
        self.catalog.delIndex('path')
        self.catalog.addIndex('path', 'FieldIndex')
        switchPathIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('path')
        self.assertEqual(index.__class__.__name__, 'ExtendedPathIndex')

    def testSwitchPathIndexTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('path')
        self.catalog.addIndex('path', 'FieldIndex')
        switchPathIndex(self.portal, [])
        switchPathIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('path')
        self.assertEqual(index.__class__.__name__, 'ExtendedPathIndex')

    def testSwitchPathIndexNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        switchPathIndex(self.portal, [])

    def testSwitchPathIndexNoIndex(self):
        # Should not fail if path index is missing
        self.catalog.delIndex('path')
        switchPathIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('path')
        self.assertEqual(index.__class__.__name__, 'ExtendedPathIndex')

    def testAddGetObjPositionInParentIndex(self):
        # Should add getObjPositionInParent index
        self.catalog.delIndex('getObjPositionInParent')
        addGetObjPositionInParentIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('getObjPositionInParent')
        self.assertEqual(index.__class__.__name__, 'FieldIndex')

    def testAddGetObjPositionInParentIndexTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('getObjPositionInParent')
        addGetObjPositionInParentIndex(self.portal, [])
        addGetObjPositionInParentIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('getObjPositionInParent')
        self.assertEqual(index.__class__.__name__, 'FieldIndex')

    def testAddGetObjPositionInParentIndexNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        addGetObjPositionInParentIndex(self.portal, [])

    def testAddGetObjSizeMetadata(self):
        # Should add getObjSize to schema
        self.catalog.delColumn('getObjSize')
        addGetObjSizeMetadata(self.portal, [])
        self.failUnless('getObjSize' in self.catalog.schema())

    def testAddGetObjSizeMetadataTwice(self):
        # Should not fail if migrated again
        self.catalog.delColumn('getObjSize')
        addGetObjSizeMetadata(self.portal, [])
        addGetObjSizeMetadata(self.portal, [])
        self.failUnless('getObjSize' in self.catalog.schema())

    def testAddGetObjSizeMetadataNoCatalog(self):
        # Should not fail if catalog is missing
        self.portal._delObject('portal_catalog')
        addGetObjSizeMetadata(self.portal, [])

    def testUpdateNavTreeProperties(self):
        # Should add new navtree_properties
        self.removeNavTreeProperty('typesToList')
        self.removeNavTreeProperty('sortAttribute')
        self.removeNavTreeProperty('sortOrder')
        self.removeNavTreeProperty('sitemapDepth')
        self.removeNavTreeProperty('showAllParents')
        self.failIf(self.properties.navtree_properties.hasProperty('typesToList'))
        updateNavTreeProperties(self.portal, [])
        self.failUnless(self.properties.navtree_properties.hasProperty('typesToList'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sortAttribute'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sortOrder'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sitemapDepth'))
        self.failUnless(self.properties.navtree_properties.hasProperty('showAllParents'))

    def testUpdateNavTreePropertiesTwice(self):
        # Should not fail if migrated again
        self.removeNavTreeProperty('typesToList')
        self.removeNavTreeProperty('sortAttribute')
        self.removeNavTreeProperty('sortOrder')
        self.removeNavTreeProperty('sitemapDepth')
        self.removeNavTreeProperty('showAllParents')
        self.failIf(self.properties.navtree_properties.hasProperty('typesToList'))
        updateNavTreeProperties(self.portal, [])
        updateNavTreeProperties(self.portal, [])
        self.failUnless(self.properties.navtree_properties.hasProperty('typesToList'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sortAttribute'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sortOrder'))
        self.failUnless(self.properties.navtree_properties.hasProperty('sitemapDepth'))
        self.failUnless(self.properties.navtree_properties.hasProperty('showAllParents'))

    def testUpdateNavTreePropertiesNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        updateNavTreeProperties(self.portal, [])

    def testUpdateNavTreePropertiesNoSheet(self):
        # Should not fail if navtree_properties is missing
        self.properties._delObject('navtree_properties')
        updateNavTreeProperties(self.portal, [])

    def testAddSitemapAction(self):
        # Should add the sitemap action
        self.removeActionFromTool('sitemap')
        self.failIf('sitemap' in [x.id for x in self.actions.listActions()])
        addSitemapAction(self.portal, [])
        self.failUnless('sitemap' in [x.id for x in self.actions.listActions()])

    def testAddSitemapActionTwice(self):
        # Should not fail if migrated again
        self.removeActionFromTool('sitemap')
        self.failIf('sitemap' in [x.id for x in self.actions.listActions()])
        addSitemapAction(self.portal, [])
        addSitemapAction(self.portal, [])
        self.failUnless('sitemap' in [x.id for x in self.actions.listActions()])

    def testAddSitemapActionNoTool(self):
        # Should not fail if portal_actions is missing
        self.portal._delObject('portal_actions')
        addSitemapAction(self.portal, [])

    def testAddDefaultGroups(self):
        # Should create the admin and reviewer groups
        self.setRoles(['Manager'])
        self.groups.removeGroups(('Administrators', 'Reviewers'))
        addDefaultGroups(self.portal, [])
        self.failUnless('Administrators' in self.groups.listGroupIds())
        self.failUnless('Reviewers' in self.groups.listGroupIds())

    def testAddDefaultGroupsDoesntCreateWorkspaces(self):
        # Should not create workspaces even if enabled
        self.setRoles(['Manager'])
        self.groups.groupWorkspaceCreationFlag = True
        self.groups.removeGroups(('Administrators', 'Reviewers'))
        addDefaultGroups(self.portal, [])
        self.failUnless('Administrators' in self.groups.listGroupIds())
        self.failUnless('Reviewers' in self.groups.listGroupIds())

    def testAddDefaultGroupsTwice(self):
        # Should not fail if migrated again
        self.setRoles(['Manager'])
        self.portal.portal_groups.removeGroups(('Administrators', 'Reviewers'))
        out = []
        addDefaultGroups(self.portal, out)
        # Reports about the 2 new groups that were added.
        self.assertEquals(len(out), 2)
        addDefaultGroups(self.portal, out)
        # Doesn't add any new groups.
        self.assertEquals(len(out), 2)
        self.failUnless('Administrators' in self.groups.listGroupIds())
        self.failUnless('Reviewers' in self.groups.listGroupIds())

    def testAddDefaultGroupsNoTool(self):
        # Should not fail if portal_groups is missing
        self.setRoles(['Manager'])
        self.portal._delObject('portal_groups')
        addDefaultGroups(self.portal, [])

    def testReindexCatalog(self):
        # Should rebuild the catalog
        self.folder.invokeFactory('Document', id='doc', title='Foo')
        self.folder.doc.setTitle('Bar')
        self.assertEqual(len(self.catalog(Title='Foo')), 1)
        reindexCatalog(self.portal, [])
        self.assertEqual(len(self.catalog(Title='Foo')), 0)
        self.assertEqual(len(self.catalog(Title='Bar')), 1)

    def testInstallCSSandJSRegistries(self):
        # Should install ResourceRegistries
        self.setRoles(('Manager',))
        self.uninstallProduct('ResourceRegistries')
        self.portal.manage_delObjects(['portal_css', 'portal_javascripts'])
        installCSSandJSRegistries(self.portal, [])
        self.failUnless('portal_css' in self.portal.objectIds())
        self.failUnless('portal_javascripts' in self.portal.objectIds())

    def testInstallCSSandJSRegistriesTwice(self):
        # Should not fail if migrated again
        self.setRoles(('Manager',))
        self.uninstallProduct('ResourceRegistries')
        self.portal.manage_delObjects(['portal_css', 'portal_javascripts'])
        installCSSandJSRegistries(self.portal, [])
        installCSSandJSRegistries(self.portal, [])
        self.failUnless('portal_css' in self.portal.objectIds())
        self.failUnless('portal_javascripts' in self.portal.objectIds())

    def testInstallCSSandJSRegistriesNoTools(self):
        # Should not fail if tools are missing
        self.portal._delObject('portal_css')
        self.portal._delObject('portal_javascripts')
        installCSSandJSRegistries(self.portal, [])

    def testAddUnfriendlyTypesSiteProperty(self):
        # Should add the types_not_searched property
        self.removeSiteProperty('types_not_searched')
        self.failIf(self.properties.site_properties.hasProperty('types_not_searched'))
        addUnfriendlyTypesSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('types_not_searched'))

    def testAddUnfriendlyTypesSitePropertyTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('types_not_searched')
        self.failIf(self.properties.site_properties.hasProperty('types_not_searched'))
        addUnfriendlyTypesSiteProperty(self.portal, [])
        addUnfriendlyTypesSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('types_not_searched'))

    def testAddUnfriendlyTypesSitePropertyNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addUnfriendlyTypesSiteProperty(self.portal, [])

    def testAddUnfriendlyTypesSitePropertyNoSheet(self):
        # Should not fail if site_properties is missing
        self.properties._delObject('site_properties')
        addUnfriendlyTypesSiteProperty(self.portal, [])

    def testAddNonDefaultPageTypesSiteProperty(self):
        # Should add the non_default_page_types property
        self.removeSiteProperty('non_default_page_types')
        self.failIf(self.properties.site_properties.hasProperty('non_default_page_types'))
        addNonDefaultPageTypesSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('non_default_page_types'))

    def testAddNonDefaultPageTypesSitePropertyTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('non_default_page_types')
        self.failIf(self.properties.site_properties.hasProperty('non_default_page_types'))
        addNonDefaultPageTypesSiteProperty(self.portal, [])
        addNonDefaultPageTypesSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('non_default_page_types'))

    def testAddNonDefaultPageTypesSitePropertyNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addNonDefaultPageTypesSiteProperty(self.portal, [])

    def testAddNonDefaultPageTypesSitePropertyNoSheet(self):
        # Should not fail if site_properties is missing
        self.properties._delObject('site_properties')
        addNonDefaultPageTypesSiteProperty(self.portal, [])

    def testRemovePortalTabsActions(self):
        # Should remove the news and Members actions
        self.addActionToTool('Members', 'portal_tabs')
        self.addActionToTool('news', 'portal_tabs')
        removePortalTabsActions(self.portal, [])
        live_actions = self.actions.listActions()
        self.failIf([x for x in live_actions if x.id == 'Members' and x.visible])
        self.failIf([x for x in live_actions if x.id == 'news' and x.visible])

    def testRemovePortalTabsActionsNoActions(self):
        # Should not fail if the actions are already gone
        self.removeActionFromTool('Members')
        self.removeActionFromTool('news')
        removePortalTabsActions(self.portal, [])

    def testRemovePortalTabsActionsNoTool(self):
        # Should not fail if portal_actions is missing
        self.portal._delObject('portal_actions')
        removePortalTabsActions(self.portal, [])

    def testRemovePortalTabsActionsTwice(self):
        # Should not fail if migrated twice
        removePortalTabsActions(self.portal, [])
        removePortalTabsActions(self.portal, [])
        live_actions = self.actions.listActions()
        self.failIf([x for x in live_actions if x.id == 'Members' and x.visible])
        self.failIf([x for x in live_actions if x.id == 'Members' and x.visible])

    def testAddNewsFolder(self):
        #Should add the new news folder with appropriate default view settings
        self.portal._delObject('news')
        self.failIf('news' in self.portal.objectIds())
        addNewsFolder(self.portal, [])
        self.failUnless('news' in self.portal.objectIds())
        news = getattr(self.portal.aq_base, 'news')
        self.assertEqual(news._getPortalTypeName(), 'Large Plone Folder')
        self.assertEqual(list(news.getProperty('default_page')), ['news_topic', 'news_listing','index_html'])
        self.assertEqual(list(news.getImmediatelyAddableTypes()),['News Item'])
        self.assertEqual(list(news.getLocallyAllowedTypes()),['News Item'])
        self.assertEqual(news.getConstrainTypesMode(), 1)

    def testAddNewsFolderTwice(self):
        #Should not fail when done twice
        self.portal._delObject('news')
        self.failIf('news' in self.portal.objectIds())
        addNewsFolder(self.portal, [])
        addNewsFolder(self.portal, [])
        self.failUnless('news' in self.portal.objectIds())

    def testAddNewsTopic(self):
        #Should add the default view for the news folder, a topic
        self.portal._delObject('news')
        addNewsFolder(self.portal, [])
        news = self.portal.news
        self.failIf('news_topic' in news.objectIds())
        addNewsTopic(self.portal, [])
        self.failUnless('news_topic' in news.objectIds())
        topic = getattr(news.aq_base, 'news_topic')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')

    def testAddNewsTopicTwice(self):
        #Should not fail if done twice
        self.portal._delObject('news')
        addNewsFolder(self.portal, [])
        news = self.portal.news
        self.failIf('news_topic' in news.objectIds())
        addNewsTopic(self.portal, [])
        addNewsTopic(self.portal, [])
        self.failUnless('news_topic' in news.objectIds())

    def testAddNewsTopicNoATCT(self):
        #Should not do anything unless ATCT is installed
        self.portal._delObject('news')
        addNewsFolder(self.portal, [])
        news = self.portal.news
        self.portal._delObject('portal_atct')
        addNewsTopic(self.portal, [])
        self.failUnless('news_topic' not in news.objectIds())

    def testAddEventsFolder(self):
        #Should add the new events folder with appropriate default view settings
        self.portal._delObject('events')
        self.failIf('events' in self.portal.objectIds())
        addEventsFolder(self.portal, [])
        self.failUnless('events' in self.portal.objectIds())
        events = getattr(self.portal.aq_base, 'events')
        self.assertEqual(events._getPortalTypeName(), 'Large Plone Folder')
        self.assertEqual(list(events.getProperty('default_page')), ['events_topic', 'events_listing','index_html'])
        self.assertEqual(list(events.getImmediatelyAddableTypes()),['Event'])
        self.assertEqual(list(events.getLocallyAllowedTypes()),['Event'])
        self.assertEqual(events.getConstrainTypesMode(), 1)

    def testAddEventsFolderTwice(self):
        #Should not fail when done twice
        self.portal._delObject('events')
        self.failIf('events' in self.portal.objectIds())
        addEventsFolder(self.portal, [])
        addEventsFolder(self.portal, [])
        self.failUnless('events' in self.portal.objectIds())

    def testAddEventsTopic(self):
        #Should add the default view for the events folder, a topic
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        events = self.portal.events
        self.failIf('events_topic' in events.objectIds())
        addEventsTopic(self.portal, [])
        self.failUnless('events_topic' in events.objectIds())
        topic = getattr(events.aq_base, 'events_topic')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')

    def testAddEventsTopicTwice(self):
        #Should not fail if done twice
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        events = self.portal.events
        self.failIf('events_topic' in events.objectIds())
        addEventsTopic(self.portal, [])
        addEventsTopic(self.portal, [])
        self.failUnless('events_topic' in events.objectIds())

    def testAddEventsTopicNoATCT(self):
        #Should not do anything unless ATCT is installed
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        events = self.portal.events
        self.portal._delObject('portal_atct')
        addEventsTopic(self.portal, [])
        self.failUnless('events_topic' not in events.objectIds())

    def testAddExclude_from_navMetadata(self):
        # Should add getObjSize to schema
        self.catalog.delColumn('exclude_from_nav')
        addExclude_from_navMetadata(self.portal, [])
        self.failUnless('exclude_from_nav' in self.catalog.schema())

    def testAddExclude_from_navMetadataTwice(self):
        # Should not fail if migrated again
        self.catalog.delColumn('exclude_from_nav')
        addExclude_from_navMetadata(self.portal, [])
        addExclude_from_navMetadata(self.portal, [])
        self.failUnless('exclude_from_nav' in self.catalog.schema())

    def testAddExclude_from_navMetadataNoCatalog(self):
        # Should not fail if catalog is missing
        self.portal._delObject('portal_catalog')
        addExclude_from_navMetadata(self.portal, [])

    def testAddIs_FolderishMetadata(self):
        # Should add is_folderish to schema
        try:
            self.catalog.delColumn('is_folderish')
        except (AttributeError, ValueError):
            pass
        addIs_FolderishMetadata(self.portal, [])
        self.failUnless('is_folderish' in self.catalog.schema())

    def testAddIs_FolderishMetadataTwice(self):
        # Should not fail if migrated again
        try:
            self.catalog.delColumn('is_folderish')
        except (AttributeError, ValueError):
            pass
        addIs_FolderishMetadata(self.portal, [])
        addIs_FolderishMetadata(self.portal, [])
        self.failUnless('is_folderish' in self.catalog.schema())

    def testAddIs_FolderishMetadataNoCatalog(self):
        # Should not fail if catalog is missing
        try:
            self.portal._delObject('portal_catalog')
        except (AttributeError, ValueError):
            pass
        addIs_FolderishMetadata(self.portal, [])

    def testAddEditContentActions(self):
        # Should add the edit-content actions
        editActions = ('cut', 'copy', 'paste', 'delete', 'batch')
        for a in editActions:
            self.removeActionFromTool(a)
        addEditContentActions(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testAddEditContentActionsTwice(self):
        # Should add the edit-content actions
        editActions = ('cut', 'copy', 'paste', 'delete', 'batch')
        for a in editActions:
            self.removeActionFromTool(a)
        addEditContentActions(self.portal, [])
        addEditContentActions(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testAddEditContentActionsNoTool(self):
        # Should not fail if portal_actions is missing
        self.portal._delObject('portal_actions')
        addEditContentActions(self.portal, [])

    def testIndexMembersFolder(self):
        # Members folder should be cataloged
        members = self.membership.getMembersFolder()
        members.unindexObject()
        indexMembersFolder(self.portal, [])
        self.failUnless(self.catalog(id='Members'))

    def testIndexMembersFolderTwice(self):
        # Should not fail if migrated again
        members = self.membership.getMembersFolder()
        members.unindexObject()
        indexMembersFolder(self.portal, [])
        indexMembersFolder(self.portal, [])
        self.failUnless(self.catalog(id='Members'))

    def testIndexMembersFolderNoCatalog(self):
        # Should not fail if catalog is missing
        self.portal._delObject('portal_catalog')
        indexMembersFolder(self.portal, [])

    def testIndexMembersFolderNoMembersFolder(self):
        # Should not fail if Members folder is missing
        self.portal._delObject('Members')
        indexMembersFolder(self.portal, [])

    def testMigrateDateIndexes(self):
        # Should migrate date related indexes
        self.catalog.delIndex('effective')
        self.catalog.addIndex('effective', 'FieldIndex')
        self.assertEqual(migrateDateIndexes(self.portal, []), 1)
        self.assertEqual(self.catalog.Indexes['effective'].__class__.__name__,
                         'DateIndex')

    def testMigrateDateIndexesTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('effective')
        self.catalog.addIndex('effective', 'FieldIndex')
        self.assertEqual(migrateDateIndexes(self.portal, []), 1)
        self.assertEqual(migrateDateIndexes(self.portal, []), 0)
        self.assertEqual(self.catalog.Indexes['effective'].__class__.__name__,
                         'DateIndex')

    def testMigrateDateIndexesNoCatalog(self):
        # Should not fail if catalog is missing
        self.portal._delObject('portal_catalog')
        self.assertEqual(migrateDateIndexes(self.portal, []), 0)

    def testMigrateDateIndexesNoIndex(self):
        # Should not fail if an index is missing
        self.catalog.delIndex('effective')
        self.assertEqual(migrateDateIndexes(self.portal, []), 1)
        self.assertEqual(self.catalog.Indexes['effective'].__class__.__name__,
                         'DateIndex')

    def testMigrateDateRangeIndexes(self):
        # Should migrate date related indexes
        self.catalog.delIndex('effectiveRange')
        self.catalog.addIndex('effectiveRange', 'FieldIndex')
        self.assertEqual(migrateDateRangeIndexes(self.portal, []), 1)
        self.assertEqual(self.catalog.Indexes['effectiveRange'].__class__.__name__,
                         'DateRangeIndex')

    def testMigrateDateRangeIndexesTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('effectiveRange')
        self.catalog.addIndex('effectiveRange', 'FieldIndex')
        self.assertEqual(migrateDateRangeIndexes(self.portal, []), 1)
        self.assertEqual(migrateDateRangeIndexes(self.portal, []), 0)
        self.assertEqual(self.catalog.Indexes['effectiveRange'].__class__.__name__,
                         'DateRangeIndex')

    def testMigrateDateRangeIndexesNoCatalog(self):
        # Should not fail if catalog is missing
        self.portal._delObject('portal_catalog')
        self.assertEqual(migrateDateRangeIndexes(self.portal, []), 0)

    def testMigrateDateRangeIndexesNoIndex(self):
        # Should not fail if an index is missing
        self.catalog.delIndex('effectiveRange')
        self.assertEqual(migrateDateRangeIndexes(self.portal, []), 1)
        self.assertEqual(self.catalog.Indexes['effectiveRange'].__class__.__name__,
                         'DateRangeIndex')

    def testAddSortable_TitleIndex(self):
        # Should add sortable_title index
        self.catalog.delIndex('sortable_title')
        addSortable_TitleIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('sortable_title')
        self.assertEqual(index.__class__.__name__, 'FieldIndex')

    def testAddSortable_TitleIndexTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('sortable_title')
        addSortable_TitleIndex(self.portal, [])
        addSortable_TitleIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('sortable_title')
        self.assertEqual(index.__class__.__name__, 'FieldIndex')

    def testAddSortable_TitleIndexNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        addSortable_TitleIndex(self.portal, [])

    def testAddDefaultTypesToPortalFactory(self):
        # Should add user-visible ATContentTypes types to portal_factory
        self.factory.manage_setPortalFactoryTypes(listOfTypeIds = [])
        addDefaultTypesToPortalFactory(self.portal, [])
        types = self.factory.getFactoryTypes().keys()
        for metaType in ('Document', 'Event', 'File', 'Folder', 'Image',
                         'Folder', 'Large Plone Folder', 'Link', 'News Item',
                         'Topic'):
            self.failUnless(metaType in types)

    def testAddDefaultTypesToPortalFactoryTwice(self):
        # Should not fail if migrated again
        self.factory.manage_setPortalFactoryTypes(listOfTypeIds = [])
        addDefaultTypesToPortalFactory(self.portal, [])
        addDefaultTypesToPortalFactory(self.portal, [])
        types = self.factory.getFactoryTypes().keys()
        for metaType in ('Document', 'Event', 'File', 'Folder', 'Image',
                         'Folder', 'Large Plone Folder', 'Link', 'News Item',
                         'Topic'):
            self.failUnless(metaType in types)

    def testAddDefaultTypesToPortalFactoryNoTool(self):
        # Should not fail if portal_factory is missing
        self.portal._delObject('portal_factory')
        addDefaultTypesToPortalFactory(self.portal, [])

    def testAddDisableFolderSectionsSiteProperty(self):
        # Should add the disable_folder_sections property
        self.removeSiteProperty('disable_folder_sections')
        self.failIf(self.properties.site_properties.hasProperty('disable_folder_sections'))
        addDisableFolderSectionsSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('disable_folder_sections'))

    def testAddDisableFolderSectionsSitePropertyTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('disable_folder_sections')
        self.failIf(self.properties.site_properties.hasProperty('disable_folder_sections'))
        addDisableFolderSectionsSiteProperty(self.portal, [])
        addDisableFolderSectionsSiteProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('disable_folder_sections'))

    def testAddDisableFolderSectionsSitePropertyNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addDisableFolderSectionsSiteProperty(self.portal, [])

    def testAddDisableFolderSectionsSitePropertyNoSheet(self):
        # Should not fail if site_properties is missing
        self.properties._delObject('site_properties')
        addDisableFolderSectionsSiteProperty(self.portal, [])

    def testAddSiteRootViewTemplates(self):
        self.portal.manage_delProperties(['selectable_views'])
        addSiteRootViewTemplates(self.portal, [])
        views = self.portal.getProperty('selectable_views', None)
        self.failUnless(type(views) in (types.ListType, types.TupleType,))
        self.failUnless('folder_listing' in views)
        self.failUnless('news_listing' in views)

    def testAddSiteRootViewTemplatesTwice(self):
        self.portal.manage_delProperties(['selectable_views'])
        addSiteRootViewTemplates(self.portal, [])
        addSiteRootViewTemplates(self.portal, [])
        views = self.portal.getProperty('selectable_views', None)
        self.failUnless(type(views) in (types.ListType, types.TupleType,))
        self.failUnless('folder_listing' in views)
        self.failUnless('news_listing' in views)

    def testAddSiteRootViewTemplatesPropertyExists(self):
        self.portal.manage_changeProperties(selectable_views = ['one', 'two'])
        addSiteRootViewTemplates(self.portal, [])
        views = self.portal.getProperty('selectable_views', None)
        self.failUnless(type(views) in (types.ListType, types.TupleType,))
        self.failUnless(len(views) == 2)
        self.failUnless('one' in views)
        self.failUnless('two' in views)

    def testAddMemberdataHome_Page(self):
        # Should add the home_page property
        self.removeMemberdataProperty('home_page')
        self.failIf(self.portal_memberdata.hasProperty('home_page'))
        addMemberdataHome_Page(self.portal, [])
        self.failUnless(self.portal_memberdata.hasProperty('home_page'))

    def testAddMemberdataHome_PageTwice(self):
        # Should not fail if migrated again
        self.removeMemberdataProperty('home_page')
        self.failIf(self.portal_memberdata.hasProperty('home_page'))
        addMemberdataHome_Page(self.portal, [])
        addMemberdataHome_Page(self.portal, [])
        self.failUnless(self.portal_memberdata.hasProperty('home_page'))

    def testAddMemberdataHome_PageNoTool(self):
        # Should not fail if portal_memberdata is missing
        self.portal._delObject('portal_memberdata')
        addMemberdataHome_Page(self.portal, [])

    def testAddMemberdataLocation(self):
        # Should add the location property
        self.removeMemberdataProperty('location')
        self.failIf(self.portal_memberdata.hasProperty('location'))
        addMemberdataLocation(self.portal, [])
        self.failUnless(self.portal_memberdata.hasProperty('location'))

    def testAddMemberdataLocationTwice(self):
        # Should not fail if migrated again
        self.removeMemberdataProperty('location')
        self.failIf(self.portal_memberdata.hasProperty('location'))
        addMemberdataLocation(self.portal, [])
        addMemberdataLocation(self.portal, [])
        self.failUnless(self.portal_memberdata.hasProperty('location'))

    def testAddMemberdataLocationNoTool(self):
        # Should not fail if portal_memberdata is missing
        self.portal._delObject('portal_memberdata')
        addMemberdataLocation(self.portal, [])

    def testAddMemberdataDescription(self):
        # Should add the description property
        self.removeMemberdataProperty('description')
        self.failIf(self.portal_memberdata.hasProperty('description'))
        addMemberdataDescription(self.portal, [])
        self.failUnless(self.portal_memberdata.hasProperty('description'))

    def testAddMemberdataDescriptionTwice(self):
        # Should not fail if migrated again
        self.removeMemberdataProperty('description')
        self.failIf(self.portal_memberdata.hasProperty('description'))
        addMemberdataDescription(self.portal, [])
        addMemberdataDescription(self.portal, [])
        self.failUnless(self.portal_memberdata.hasProperty('description'))

    def testAddMemberdataDescriptionNoTool(self):
        # Should not fail if portal_memberdata is missing
        self.portal._delObject('portal_memberdata')
        addMemberdataDescription(self.portal, [])

    def testAddMemberdataLanguage(self):
        # Should add the home_page property
        self.removeMemberdataProperty('language')
        self.failIf(self.portal_memberdata.hasProperty('language'))
        addMemberdataLanguage(self.portal, [])
        self.failUnless(self.portal_memberdata.hasProperty('language'))

    def testAddMemberdataLanguageTwice(self):
        # Should not fail if migrated again
        self.removeMemberdataProperty('language')
        self.failIf(self.portal_memberdata.hasProperty('language'))
        addMemberdataLanguage(self.portal, [])
        addMemberdataLanguage(self.portal, [])
        self.failUnless(self.portal_memberdata.hasProperty('language'))

    def testAddMemberdataLanguageNoTool(self):
        # Should not fail if portal_memberdata is missing
        self.portal._delObject('portal_memberdata')
        addMemberdataLanguage(self.portal, [])

    def testAlterChangeStateActionCondition(self):
        # The condition for the change_state action should not be blank
        # and the permission should be set to View
        new_actions = self.actions._cloneActions()
        for action in new_actions:
            if action.getId() == 'change_state':
                action.condition = ''
                action.permissions = ('Modify portal contents',)
        self.actions._actions = new_actions

        actions = [x for x in self.actions.listActions() if x.id == 'change_state']
        self.assertEqual(actions[0].condition, '')
        self.assertEqual(actions[0].permissions, ('Modify portal contents',))
        # Modify
        alterChangeStateActionCondition(self.portal, [])
        actions = [x for x in self.actions.listActions() if x.id == 'change_state']
        self.assertEqual(len(actions),1)
        action = actions[0]
        action_text = getattr(action.condition, 'text','')
        self.failUnless(action_text!='')
        self.assertEqual(action.permissions, ('View',))

    def testAlterChangeStateActionConditionTwice(self):
        # The migration should work if performed twice
        alterChangeStateActionCondition(self.portal, [])
        alterChangeStateActionCondition(self.portal, [])
        actions = [x for x in self.actions.listActions() if x.id == 'change_state']
        self.assertEqual(len(actions),1)
        action = actions[0]
        action_text = getattr(action.condition, 'text','')
        self.failUnless(action_text!='')
        self.assertEqual(action.permissions, ('View',))

    def testAlterChangeStateActionConditionNoAction(self):
        # The migration should add a new action if the action is missing
        self.removeActionFromTool('change_state')
        alterChangeStateActionCondition(self.portal, [])
        actions = [x for x in self.actions.listActions() if x.id == 'change_state']
        self.assertEqual(len(actions),1)
        action = actions[0]
        action_text = getattr(action.condition, 'text','')
        self.failUnless(action_text!='')
        self.assertEqual(action.permissions, ('View',))

    def testAlterChangeStateActionConditionNoTool(self):
        # The migration should work if the tool is missing
        self.portal._delObject('portal_actions')
        alterChangeStateActionCondition(self.portal, [])

    def testFixFolderButtonsActions(self):
        # The condition for the change_state action should not be blank
        # and the permission should be set to View
        current_actions = self.actions._cloneActions()
        for action in current_actions:
            if action.getId() in ['copy', 'cut'] and action.category == 'folder_buttons':
                action.condition = ''
                action.permissions = ('View management screens',)
        self.actions._actions = current_actions

        actions = [x for x in self.actions.listActions() if
                    x.id in ['copy', 'cut'] and x.category == 'folder_buttons']
        self.assertEqual(len(actions),2)
        self.assertEqual(actions[0].condition, '')
        self.assertEqual(actions[1].condition, '')
        self.assertEqual(actions[0].permissions, ('View management screens',))
        self.assertEqual(actions[1].permissions, ('View management screens',))
        # Modify
        fixFolderButtonsActions(self.portal, [])
        actions = [x for x in self.actions.listActions() if
                    x.id in ['copy', 'cut'] and x.category == 'folder_buttons']
        self.assertEqual(len(actions),2)
        for action in actions:
            if action.getId() == 'cut':
                self.failUnless(action.condition.text!='')
            else:
                action_text = getattr(action.condition, 'text','')
                self.assertEqual(action_text, '', 'Bad condition was: %s'%action_text)
            self.assertEqual(action.permissions, ('Copy or Move',))

    def testFixFolderButtonsActionsTwice(self):
        fixFolderButtonsActions(self.portal, [])
        fixFolderButtonsActions(self.portal, [])
        actions = [x for x in self.actions.listActions() if
                    x.id in ['copy', 'cut'] and x.category == 'folder_buttons']
        self.assertEqual(len(actions),2)
        for action in actions:
            if action.getId() == 'cut':
                action_text = getattr(action.condition, 'text','')
                self.failUnless(action_text!='')
            else:
                action_text = getattr(action.condition, 'text','')
                self.assertEqual(action_text, '', 'Bad condition was: %s'%action_text)
            self.assertEqual(action.permissions, ('Copy or Move',))

    def testFixFolderButtonsActionsNoCutAction(self):
        # The migration should add new actions if the actions are missing
        self.removeActionFromTool('cut')
        fixFolderButtonsActions(self.portal, [])
        actions = [x for x in self.actions.listActions() if
                    x.id == 'cut' and x.category == 'folder_buttons']
        self.assertEqual(len(actions),1)
        for action in actions:
            action_text = getattr(action.condition, 'text','')
            self.failUnless(action_text!='')
            self.assertEqual(action.permissions, ('Copy or Move',))

    def testFixFolderButtonsActionsNoCopyAction(self):
        # The migration should add new actions if the actions are missing
        self.removeActionFromTool('copy')
        fixFolderButtonsActions(self.portal, [])
        actions = [x for x in self.actions.listActions() if
                    x.id == 'copy' and x.category == 'folder_buttons']
        self.assertEqual(len(actions),1)
        for action in actions:
            action_text = getattr(action.condition, 'text','')
            self.assertEqual(action_text, '', 'Bad condition was: %s'%action_text)
            self.assertEqual(action.permissions, ('Copy or Move',))

    def testFixFolderButtonsActionsNoTool(self):
        # The migration should work if the tool is missing
        self.portal._delObject('portal_actions')
        fixFolderButtonsActions(self.portal, [])

    def testAddTypesUseViewActionInListingsProperty(self):
        # Should add the typesUseViewActionInListings property
        self.removeSiteProperty('typesUseViewActionInListings')
        self.failIf(self.properties.site_properties.hasProperty('typesUseViewActionInListings'))
        addTypesUseViewActionInListingsProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('typesUseViewActionInListings'))

    def testAddTypesUseViewActionInListingsPropertyTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('typesUseViewActionInListings')
        self.failIf(self.properties.site_properties.hasProperty('typesUseViewActionInListings'))
        addTypesUseViewActionInListingsProperty(self.portal, [])
        addTypesUseViewActionInListingsProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('typesUseViewActionInListings'))

    def testAddTypesUseViewActionInListingsPropertyNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addTypesUseViewActionInListingsProperty(self.portal, [])

    def testAddTypesUseViewActionInListingsPropertyNoSheet(self):
        # Should not fail if site_properties is missing
        self.properties._delObject('site_properties')
        addTypesUseViewActionInListingsProperty(self.portal, [])

    def testSwitchToExpirationDateMetadata(self):
        # This should delete ExpiresDate and add ExpirationDate to the catalog
        # schema.
        self.catalog.addColumn('ExpiresDate')
        self.catalog.delColumn('ExpirationDate')
        switchToExpirationDateMetadata(self.portal, [])
        self.failUnless('ExpirationDate' in self.catalog.schema())
        self.failUnless('ExpiresDate' not in self.catalog.schema())

    def testSwitchToExpirationDateMetadataTwice(self):
        # Should not fail if migrated again
        self.catalog.addColumn('ExpiresDate')
        self.catalog.delColumn('ExpirationDate')
        switchToExpirationDateMetadata(self.portal, [])
        switchToExpirationDateMetadata(self.portal, [])
        self.failUnless('ExpirationDate' in self.catalog.schema())
        self.failUnless('ExpiresDate' not in self.catalog.schema())

    def testSwitchToExpirationDateMetadataNoCatalog(self):
        # Should not fail if the catalog is missing
        self.portal._delObject('portal_catalog')
        switchToExpirationDateMetadata(self.portal, [])

    def testChangePloneSetupActionToSiteSetup(self):
        # The plone_setup action should be renamed to 'Site Setup'
        new_actions = self.actions._cloneActions()
        for action in new_actions:
            if action.getId() == 'plone_setup':
                action.title = 'Plone Setup'
        self.actions._actions = new_actions

        actions = [x for x in self.actions.listActions() if x.id == 'plone_setup']
        self.assertEqual(actions[0].title, 'Plone Setup')
        # Modify
        changePloneSetupActionToSiteSetup(self.portal, [])
        actions = [x for x in self.actions.listActions() if x.id == 'plone_setup' and x.category == 'user']
        self.assertEqual(len(actions),1)
        action = actions[0]
        self.assertEqual(action.title, 'Site Setup')

    def testChangePloneSetupActionToSiteSetupTwice(self):
        # The migration should work if performed twice
        changePloneSetupActionToSiteSetup(self.portal, [])
        changePloneSetupActionToSiteSetup(self.portal, [])
        actions = [x for x in self.actions.listActions() if x.id == 'plone_setup' and x.category == 'user']
        self.assertEqual(len(actions),1)
        action = actions[0]
        self.assertEqual(action.title, 'Site Setup')

    def testChangePloneSetupActionToSiteSetupNoAction(self):
        # The migration should add a new action if the action is missing
        self.removeActionFromTool('plone_setup')
        changePloneSetupActionToSiteSetup(self.portal, [])
        actions = [x for x in self.actions.listActions() if x.id == 'plone_setup' and x.category == 'user']
        self.assertEqual(len(actions),1)
        action = actions[0]
        self.assertEqual(action.title, 'Site Setup')

    def testChangePloneSetupActionToSiteSetupNoTool(self):
        # The migration should work if the tool is missing
        self.portal._delObject('portal_actions')
        changePloneSetupActionToSiteSetup(self.portal, [])

    def testChangePloneSiteIcon(self):
        # The Plone Site FTI icon should be changed to site_icon
        fti = getattr(self.portal.portal_types,'Plone Site')
        fti.content_icon='folder_icon.gif'
        fti = getattr(self.portal.portal_types,'Plone Site')
        self.assertEqual(fti.content_icon, 'folder_icon.gif')

        # Modify
        changePloneSiteIcon(self.portal, [])
        fti = getattr(self.portal.portal_types,'Plone Site')
        self.assertEqual(fti.content_icon, 'site_icon.gif')

    def testChangePloneSiteIconTwice(self):
        # The migration should work if performed twice
        changePloneSiteIcon(self.portal, [])
        changePloneSiteIcon(self.portal, [])
        fti = getattr(self.portal.portal_types,'Plone Site')
        self.assertEqual(fti.content_icon, 'site_icon.gif')

    def testChangePloneSiteIconNoType(self):
        # The migration should not fail if the FTI is missing
        self.portal.portal_types._delObject('Plone Site')
        changePloneSiteIcon(self.portal, [])

    def testChangePloneSiteIconNoTool(self):
        # The migration should work if the tool is missing
        self.portal._delObject('portal_types')
        changePloneSiteIcon(self.portal, [])

    def testFixObjectPasteActionForDefaultPages(self):
        # The action for the paste object button action should detect default
        # pages and operate on the parent folder.
        current_actions = self.actions._cloneActions()
        for action in current_actions:
            if action.getId() == 'paste' and action.category == 'object_buttons':
                action.setActionExpression(Expression('string:${object_url}/object_paste'))
        self.actions._actions = current_actions
        actions = [x for x in self.actions.listActions() if
                    x.id == 'paste' and x.category == 'object_buttons']
        self.assertEqual(len(actions),1)
        self.assertEqual(actions[0].getActionExpression(), 'string:${object_url}/object_paste')
        # Modify
        fixObjectPasteActionForDefaultPages(self.portal, [])
        actions = [x for x in self.actions.listActions() if
                    x.id == 'paste' and x.category == 'object_buttons']
        self.assertEqual(len(actions),1)
        self.assertEqual(actions[0].getActionExpression(), 'python:"%s/object_paste"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)')

    def testFixObjectPasteActionForDefaultPagesTwice(self):
        # The migration should work if performed twice
        fixObjectPasteActionForDefaultPages(self.portal, [])
        fixObjectPasteActionForDefaultPages(self.portal, [])
        actions = [x for x in self.actions.listActions() if
                    x.id == 'paste' and x.category == 'object_buttons']
        self.assertEqual(len(actions),1)
        self.assertEqual(actions[0].getActionExpression(), 'python:"%s/object_paste"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)')

    def testFixObjectPasteActionForDefaultPagesNoAction(self):
        # The migration should add a new action if the action is missing
        self.removeActionFromTool('cut')
        fixObjectPasteActionForDefaultPages(self.portal, [])
        actions = [x for x in self.actions.listActions() if
                    x.id == 'paste' and x.category == 'object_buttons']
        self.assertEqual(len(actions),1)
        self.assertEqual(actions[0].getActionExpression(), 'python:"%s/object_paste"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)')

    def testFixObjectPasteActionForDefaultPagesNoTool(self):
        # The migration should work if the tool is missing
        self.portal._delObject('portal_actions')
        fixObjectPasteActionForDefaultPages(self.portal, [])

    def testFixBatchActionToggle(self):
        editActions = ('batch', 'nobatch')
        for a in editActions:
            self.removeActionFromTool(a)
        fixBatchActionToggle(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixBatchActionToggleTwice(self):
        editActions = ('batch', 'nobatch')
        for a in editActions:
            self.removeActionFromTool(a)
        fixBatchActionToggle(self.portal, [])
        fixBatchActionToggle(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixBatchActionToggleNoTool(self):
        self.portal._delObject('portal_actions')
        fixBatchActionToggle(self.portal, [])

    def testFixMyFolderAction(self):
        self.removeActionFromTool('mystuff', action_provider='portal_membership')
        fixMyFolderAction(self.portal, [])
        actions = [(x.id, x.getActionExpression()) for x in self.membership.listActions()]
        for a in actions:
            if a[0] == 'mystuff':
                self.failIf('folder_contents' in a[1])

    def testFixMyFolderActionTwice(self):
        self.removeActionFromTool('mystuff', action_provider='portal_membership')
        fixMyFolderAction(self.portal, [])
        fixMyFolderAction(self.portal, [])
        actions = [(x.id, x.getActionExpression()) for x in self.membership.listActions()]
        for a in actions:
            if a[0] == 'mystuff':
                self.failIf('folder_contents' in a[1])

    def testFixMyFolderActionNoTool(self):
        self.portal._delObject('portal_membership')
        fixMyFolderAction(self.portal, [])

    def testCSSRegistryMigration(self):
        cssreg = self.portal.portal_css
        self.failIf(hasattr(cssreg, 'stylesheets'))
        self.failIf(hasattr(cssreg, 'cookedstylesheets'))
        self.failIf(hasattr(cssreg, 'concatenatedstylesheets'))
        self.failUnless(hasattr(cssreg, 'resources'))
        self.failUnless(hasattr(cssreg, 'cookedresources'))
        self.failUnless(hasattr(cssreg, 'concatenatedresources'))

    def testJSRegistryMigration(self):
        jsreg = self.portal.portal_javascripts
        self.failIf(hasattr(jsreg, 'scripts'))
        self.failIf(hasattr(jsreg, 'cookedscripts'))
        self.failIf(hasattr(jsreg, 'concatenatedscripts'))
        self.failUnless(hasattr(jsreg, 'resources'))
        self.failUnless(hasattr(jsreg, 'cookedresources'))
        self.failUnless(hasattr(jsreg, 'concatenatedresources'))

    def testAddedFontSizeStylesheets(self):
        cssreg = self.portal.portal_css
        stylesheet_ids = cssreg.getResourceIds()
        self.failUnless('textSmall.css' in stylesheet_ids)
        self.failUnless('textLarge.css' in stylesheet_ids)

    def testaddCssQueryJS(self):
        jsreg = self.portal.portal_javascripts
        script_ids = jsreg.getResourceIds()
        self.failUnless('cssQuery.js' in script_ids)

    def testExchangePloneMenuWithDropDown(self):
        jsreg = self.portal.portal_javascripts
        script_ids = jsreg.getResourceIds()
        self.failIf('plone_menu.js' in script_ids)
        self.failUnless('dropdown.js' in script_ids)
        self.failUnless('cssQuery.js' in script_ids)

    def testRemovePlonePrefixFromStylesheets(self):
        cssreg = self.portal.portal_css
        stylesheet_ids = cssreg.getResourceIds()
        self.failIf('ploneAuthoring.css' in stylesheet_ids)
        self.failIf('ploneBase.css' in stylesheet_ids)
        self.failIf('ploneColumns.css' in stylesheet_ids)
        self.failIf('ploneDeprecated.css' in stylesheet_ids)
        self.failIf('ploneGenerated.css' in stylesheet_ids)
        self.failIf('ploneIEFixes.css' in stylesheet_ids)
        self.failIf('ploneMember.css' in stylesheet_ids)
        self.failIf('ploneMobile.css' in stylesheet_ids)
        self.failIf('ploneNS4.css' in stylesheet_ids)
        self.failIf('plonePresentation.css' in stylesheet_ids)
        self.failIf('plonePrint.css' in stylesheet_ids)
        self.failIf('plonePublic.css' in stylesheet_ids)
        self.failIf('ploneRTL.css' in stylesheet_ids)
        self.failIf('ploneTextHuge.css' in stylesheet_ids)
        self.failIf('ploneTextLarge.css' in stylesheet_ids)
        self.failIf('ploneTextSmall.css' in stylesheet_ids)
        self.failUnless('authoring.css' in stylesheet_ids)
        self.failUnless('base.css' in stylesheet_ids)
        self.failUnless('columns.css' in stylesheet_ids)
        self.failUnless('generated.css' in stylesheet_ids)
        self.failUnless('member.css' in stylesheet_ids)
        self.failUnless('mobile.css' in stylesheet_ids)
        self.failUnless('presentation.css' in stylesheet_ids)
        self.failUnless('print.css' in stylesheet_ids)
        self.failUnless('public.css' in stylesheet_ids)
        self.failUnless('RTL.css' in stylesheet_ids)
        self.failUnless('textLarge.css' in stylesheet_ids)
        self.failUnless('textSmall.css' in stylesheet_ids)
        # the only one which doesn't get renamed, because there is special
        # logic in ResourceRegistries
        self.failUnless('ploneCustom.css' in stylesheet_ids)

    def testAllowOwnerToAccessInactiveContent(self):
        # Should grant the "Access inactive ..." permission to owner
        self.portal.manage_permission(
                            AccessInactivePortalContent,
                            (), acquire=1)
        permission_on_role = [p for p in self.portal.permissionsOfRole('Owner')
            if p['name'] == AccessInactivePortalContent][0]
        self.failIf(permission_on_role['selected'])
        allowOwnerToAccessInactiveContent(self.portal,[])
        permission_on_role = [p for p in self.portal.permissionsOfRole('Owner')
            if p['name'] == AccessInactivePortalContent][0]
        self.failUnless(permission_on_role['selected'])

    def testAllowOwnerToAccessInactiveContentPreservesExisting(self):
        # Should not remove customized permissions
        self.portal.manage_permission(
                            AccessInactivePortalContent,
                            ('Member',), acquire=1)
        allowOwnerToAccessInactiveContent(self.portal,[])
        # Make sure Owner was added
        permission_on_role = [p for p in self.portal.permissionsOfRole('Owner')
            if p['name'] == AccessInactivePortalContent][0]
        self.failUnless(permission_on_role['selected'])
        # Make sure original permission was preserved
        permission_on_role = [p for p in self.portal.permissionsOfRole('Member')
            if p['name'] == AccessInactivePortalContent][0]
        self.failUnless(permission_on_role['selected'])

    def testAllowOwnerToAccessInactiveContentPreservesAcquire(self):
        # Should preserve custom acquire settings
        self.portal.manage_permission(
                            AccessInactivePortalContent,
                            ('Manager'), acquire=0)
        allowOwnerToAccessInactiveContent(self.portal,[])
        cur_perms = self.portal.permission_settings(
                            AccessInactivePortalContent)[0]
        self.failIf(cur_perms['acquire'])
        # Try again with explicitly enabled acquire
        self.portal.manage_permission(
                            AccessInactivePortalContent,
                            ('Manager'), acquire=1)
        allowOwnerToAccessInactiveContent(self.portal,[])
        cur_perms = self.portal.permission_settings(
                            AccessInactivePortalContent)[0]
        self.failUnless(cur_perms['acquire'])

    def testAllowOwnerToAccessInactiveContentTwice(self):
        # Should not fail if performed twice
        self.portal.manage_permission(
                            AccessInactivePortalContent,
                            ('Manager'), acquire=0)
        allowOwnerToAccessInactiveContent(self.portal,[])
        cur_perms1 = self.portal.permission_settings(
                            AccessInactivePortalContent)[0]
        allowOwnerToAccessInactiveContent(self.portal,[])
        cur_perms2 = self.portal.permission_settings(
                            AccessInactivePortalContent)[0]
        self.assertEqual(cur_perms1,cur_perms2)

    def testRestrictNewsTopicToPublished(self):
        # Should add a new 'published' criterion to the News topic
        self.portal._delObject('news')
        addNewsFolder(self.portal, [])
        addNewsTopic(self.portal, [])
        topic = self.portal.news.news_topic
        self.assertRaises(AttributeError, topic.getCriterion,
                            'crit__review_state_ATSimpleStringCriterion')
        restrictNewsTopicToPublished(self.portal, [])
        self.failUnless(topic.getCriterion('crit__review_state_ATSimpleStringCriterion'))

    def testRestrictNewsTopicToPublishedTwice(self):
        # Should not fail if done twice
        self.portal._delObject('news')
        addNewsFolder(self.portal, [])
        addNewsTopic(self.portal, [])
        topic = self.portal.news.news_topic
        restrictNewsTopicToPublished(self.portal, [])
        restrictNewsTopicToPublished(self.portal, [])
        self.failUnless(topic.getCriterion('crit__review_state_ATSimpleStringCriterion'))

    def testRestrictNewsTopicToPublishedNoTopic(self):
        # Should not do anything unless ATCT is installed
        self.portal._delObject('news')
        addNewsFolder(self.portal, [])
        restrictNewsTopicToPublished(self.portal, [])

    def testRestrictEventsTopicToPublished(self):
        # Should add a new 'published' criterion to the News topic
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        topic = self.portal.events.events_topic
        self.assertRaises(AttributeError, topic.getCriterion,
                            'crit__review_state_ATSimpleStringCriterion')
        restrictEventsTopicToPublished(self.portal, [])
        self.failUnless(topic.getCriterion('crit__review_state_ATSimpleStringCriterion'))

    def testRestrictEventsTopicToPublishedTwice(self):
        # Should not fail if done twice
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        topic = self.portal.events.events_topic
        restrictEventsTopicToPublished(self.portal, [])
        restrictEventsTopicToPublished(self.portal, [])
        self.failUnless(topic.getCriterion('crit__review_state_ATSimpleStringCriterion'))

    def testRestrictEventsTopicToPublishedNoTopic(self):
        # Should not do anything unless ATCT is installed
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        restrictEventsTopicToPublished(self.portal, [])

    def testAddEnableLivesearchProperty(self):
        # Should add the enable_livesearch site property
        self.removeSiteProperty('enable_livesearch')
        addEnableLivesearchProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('enable_livesearch'))

    def testAddEnableLivesearchPropertyTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('enable_livesearch')
        addEnableLivesearchProperty(self.portal, [])
        addEnableLivesearchProperty(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('enable_livesearch'))

    def testAddEnableLivesearchPropertyNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addEnableLivesearchProperty(self.portal, [])

    def testAdd3rdPartySkinPathInDefault(self):
        # Should add plone_3rdParty to skin paths
        self.removeSkinLayer('plone_3rdParty')
        add3rdPartySkinPath(self.portal, [])
        path = self.skins.getSkinPath('Plone Default')
        self.assertEqual(path[-26:], ',plone_3rdParty,cmf_legacy')

    def testAdd3rdPartySkinPathInTableless(self):
        # Should add plone_3rdParty to skin paths
        self.removeSkinLayer('plone_3rdParty', skin='Plone Tableless')
        add3rdPartySkinPath(self.portal, [])
        path = self.skins.getSkinPath('Plone Tableless')
        self.assertEqual(path[-26:], ',plone_3rdParty,cmf_legacy')

    def testAdd3rdPartySkinPathTwice(self):
        # Should not fail if migrated again
        self.removeSkinLayer('plone_3rdParty')
        add3rdPartySkinPath(self.portal, [])
        add3rdPartySkinPath(self.portal, [])
        path = self.skins.getSkinPath('Plone Default')
        self.assertEqual(path[-26:], ',plone_3rdParty,cmf_legacy')

    def testAdd3rdPartySkinPathNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_skins')
        add3rdPartySkinPath(self.portal, [])

    def testAdd3rdPartySkinPathNoLayer(self):
        # Should not fail if cmf_legacy layer is missing
        self.removeSkinLayer('cmf_legacy')
        self.removeSkinLayer('plone_3rdParty')
        add3rdPartySkinPath(self.portal, [])
        path = self.skins.getSkinPath('Plone Default')
        self.assertEqual(path[-15:], ',plone_3rdParty')

    def testAddIconForSearchSettingsConfiglet(self):
        # Should add the full_screen action icon
        self.removeActionIconFromTool('SearchSettings')
        addIconForSearchSettingsConfiglet(self.portal, [])
        self.failUnless('SearchSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForSearchSettingsConfigletTwice(self):
        # Should not fail if migrated again
        self.removeActionIconFromTool('SearchSettings')
        addIconForSearchSettingsConfiglet(self.portal, [])
        addIconForSearchSettingsConfiglet(self.portal, [])
        self.failUnless('SearchSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForSearchSettingsConfigletNoTool(self):
        # Should not fail if portal_actionicons is missing
        self.portal._delObject('portal_actionicons')
        addIconForSearchSettingsConfiglet(self.portal, [])

#    def testSanitizeCookieCrumbler(self):
#        # Should set CC properties
#        self.cc.manage_changeProperties(unauth_page='', auto_login_page='')
#        sanitizeCookieCrumbler(self.portal, [])
#        self.assertEqual(self.cc.unauth_page, 'insufficient_privileges')
#        self.assertEqual(self.cc.auto_login_page, 'login_form')

#    def testSanitizeCookieCrumblerTwice(self):
#        # Should not fail if migrated again
#        self.cc.manage_changeProperties(unauth_page='', auto_login_page='')
#        sanitizeCookieCrumbler(self.portal, [])
#        sanitizeCookieCrumbler(self.portal, [])
#        self.assertEqual(self.cc.unauth_page, 'insufficient_privileges')
#        self.assertEqual(self.cc.auto_login_page, 'login_form')

#    def testSanitizeCookieCrumblerNoTool(self):
#        # Should not fail if cookie_authentication is missing
#        self.portal._delObject('cookie_authentication')
#        sanitizeCookieCrumbler(self.portal, [])

    def testConvertNavTreeWhitelistToBlacklist(self):
        # Should add navtree_property metaTypesToList and remove typesNotToList
        # and typesToList
        self.removeNavTreeProperty('metaTypesNotToList')
        self.addNavTreeProperty('typesToList')
        self.addNavTreeProperty('typesNotToList')
        self.failIf(self.properties.navtree_properties.hasProperty('metaTypesNotToList'))
        self.failUnless(self.properties.navtree_properties.hasProperty('typesNotToList'))
        self.failUnless(self.properties.navtree_properties.hasProperty('typesToList'))
        convertNavTreeWhitelistToBlacklist(self.portal, [])
        self.failUnless(self.properties.navtree_properties.hasProperty('metaTypesNotToList'))
        self.failIf(self.properties.navtree_properties.hasProperty('typesToList'))
        self.failIf(self.properties.navtree_properties.hasProperty('typesNotToList'))

    def testConvertNavTreeWhitelistToBlacklistTwice(self):
        # Should not fail if migrated again, and should yield the same value
        self.removeNavTreeProperty('metaTypesNotToList')
        self.addNavTreeProperty('typesToList')
        self.addNavTreeProperty('typesNotToList')
        convertNavTreeWhitelistToBlacklist(self.portal, [])
        first_list = list(self.properties.navtree_properties.getProperty('metaTypesNotToList'))
        convertNavTreeWhitelistToBlacklist(self.portal, [])
        second_list= list(self.properties.navtree_properties.getProperty('metaTypesNotToList'))
        first_list.sort()
        second_list.sort()
        self.assertEqual(second_list, first_list)
        self.failIf(self.properties.navtree_properties.hasProperty('typesToList'))
        self.failIf(self.properties.navtree_properties.hasProperty('typesNotToList'))

    def testConvertNavTreeWhitelistToBlacklistUpdatesExisting(self):
        # Should add new not searchable types to existing blacklist
        self.properties.navtree_properties.manage_changeProperties(metaTypesNotToList=('nonsense1','nonsense2'))
        convertNavTreeWhitelistToBlacklist(self.portal, [])
        # Check if we preserved the original values
        self.failUnless('nonsense1' in self.properties.navtree_properties.getProperty('metaTypesNotToList'))
        self.failUnless('nonsense2' in self.properties.navtree_properties.getProperty('metaTypesNotToList'))
        # Check if we added the new values
        self.failUnless('ATCurrentAuthorCriterion' in self.properties.navtree_properties.getProperty('metaTypesNotToList'))

    def testConvertNavTreeWhitelistToBlacklistNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        convertNavTreeWhitelistToBlacklist(self.portal, [])

    def testConvertNavTreeWhitelistToBlacklistNoSheet(self):
        # Should not fail if navtree_properties is missing
        self.properties._delObject('navtree_properties')
        convertNavTreeWhitelistToBlacklist(self.portal, [])

    def testAddIsDefaultPageIndex(self):
        # Should add IsDefaultPage index
        self.catalog.delIndex('is_default_page')
        addIsDefaultPageIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('is_default_page')
        self.assertEqual(index.__class__.__name__, 'FieldIndex')

    def testAddIsDefaultPageIndexTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('is_default_page')
        addIsDefaultPageIndex(self.portal, [])
        addIsDefaultPageIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('is_default_page')
        self.assertEqual(index.__class__.__name__, 'FieldIndex')

    def testAddIsDefaultPageIndexNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        addIsDefaultPageIndex(self.portal, [])

    def testAddIsFolderishIndex(self):
        # Should add IsDefaultPage index
        self.catalog.delIndex('is_folderish')
        addIsFolderishIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('is_folderish')
        self.assertEqual(index.__class__.__name__, 'FieldIndex')
        self.failIf('is_folderish' in self.catalog.schema())

    def testAddIsFolderishIndexTwice(self):
        # Should not fail if migrated again
        self.catalog.delIndex('is_folderish')
        addIsFolderishIndex(self.portal, [])
        addIsFolderishIndex(self.portal, [])
        index = self.catalog._catalog.getIndex('is_folderish')
        self.assertEqual(index.__class__.__name__, 'FieldIndex')

    def testAddIsFolderishIndexNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        addIsFolderishIndex(self.portal, [])

    def testFixContentActionConditions(self):
        editActions = ('cut', 'paste', 'delete')
        for a in editActions:
            self.removeActionFromTool(a)
        fixContentActionConditions(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixContentActionConditionsTwice(self):
        editActions = ('cut', 'paste', 'delete')
        for a in editActions:
            self.removeActionFromTool(a)
        fixContentActionConditions(self.portal, [])
        fixContentActionConditions(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixContentActionConditionsNoTool(self):
        self.portal._delObject('portal_actions')
        fixContentActionConditions(self.portal, [])

    def testFixFolderlistingAction(self):
        fixFolderlistingAction(self.portal, [])
        self.assertEqual(self.portal.getTypeInfo().getActionObject('folder/folderlisting').getActionExpression(),
                         'string:${folder_url}/view')

    def testFixFolderlistingActionTwice(self):
        fixFolderlistingAction(self.portal, [])
        fixFolderlistingAction(self.portal, [])
        self.assertEqual(self.portal.getTypeInfo().getActionObject('folder/folderlisting').getActionExpression(),
                         'string:${folder_url}/view')

    def testFixFolderlistingActionNoTool(self):
        self.portal._delObject('portal_types')
        fixFolderlistingAction(self.portal, [])

    def testFixFolderContentsActionAgain(self):
        removeActions = ('batch', 'nobatch')
        editActions = ('folderContents',)
        for a in removeActions:
            self.addActionToTool(a,'batch')
        for a in editActions:
            self.removeActionFromTool(a)
        fixFolderContentsActionAgain(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)
        for a in removeActions:
            self.failIf(a in actions)

    def testFixFolderContentsActionAgainTwice(self):
        removeActions = ('batch', 'nobatch')
        editActions = ('folderContents',)
        for a in removeActions:
            self.addActionToTool(a,'batch')
        for a in editActions:
            self.removeActionFromTool(a)
        fixFolderContentsActionAgain(self.portal, [])
        fixFolderContentsActionAgain(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)
        for a in removeActions:
            self.failIf(a in actions)

    def testFixFolderContentsAgainWithExistingAction(self):
        editActions = ('folderContents',)
        for a in editActions:
            self.removeActionFromTool(a)
            self.addActionToTool(a,'folder')
        fixFolderContentsActionAgain(self.portal, [])
        actions = [(x.id,x.category) for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless((a,'object') in actions)
            self.failIf((a,'folder') in actions)

    def testFixFolderContentsActionAgainNoTool(self):
        self.portal._delObject('portal_actions')
        fixFolderContentsActionAgain(self.portal, [])

    def testChangePortalActionCategory(self):
        # This should change the 'view' and 'edit' actions for the Plone Site
        # FTI to have category 'object'
        edit_actions = ('view','edit')
        for action in edit_actions:
            self.removeActionFromType('Plone Site', action)
            self.addActionToType('Plone Site', action, 'folder')

        changePortalActionCategory(self.portal, [])
        fti = getattr(self.portal.portal_types, 'Plone Site')
        actions = [(x.getId(), x.category) for x in fti.listActions()]
        for a in edit_actions:
            self.failIf((a,'folder') in actions)
            self.failUnless((a,'object') in actions)

    def testChangePortalActionCategoryTwice(self):
        # The migration should work if performed twice
        edit_actions = ('view','edit')
        for action in edit_actions:
            self.removeActionFromType('Plone Site', action)
            self.addActionToType('Plone Site', action, 'folder')

        changePortalActionCategory(self.portal, [])
        changePortalActionCategory(self.portal, [])
        fti = getattr(self.portal.portal_types, 'Plone Site')
        actions = [(x.getId(), x.category) for x in fti.listActions()]
        for a in edit_actions:
            self.failIf((a,'folder') in actions)
            # Should only have one action
            self.assertEqual(actions.count((a,'object')), 1)

    def testChangePortalActionCategoryNoAction(self):
        # The migration should not fail if the action is missing
        edit_actions = ('view','edit')
        for action in edit_actions:
            self.removeActionFromType('Plone Site', action)
        changePortalActionCategory(self.portal, [])

    def testChangePortalActionCategoryNoFTI(self):
        # The migration should work if the FTI is missing
        self.portal.portal_types._delObject('Plone Site')
        changePortalActionCategory(self.portal, [])

    def testChangePortalActionCategoryNoTool(self):
        # The migration should work if the tool is missing
        self.portal._delObject('portal_types')
        changePortalActionCategory(self.portal, [])

    def testConvertPloneFTIToCMFDynamicViewFTI(self):
        ttool = self.portal.portal_types
        # Convert to old-school FTI
        migrateFTI(self.portal, 'Plone Site', None,
                   'Factory-based Type Information')
        self.assertEqual(getattr(ttool, 'Plone Site').meta_type,
                         'Factory-based Type Information')
        # Convert back
        convertPloneFTIToCMFDynamicViewFTI(self.portal, [])
        self.assertEqual(self.portal.getTypeInfo().meta_type,
                         'Factory-based Type Information with dynamic views')

    def testConvertPloneFTIToCMFDynamicViewFTIConvertsViews(self):
        ttool = self.portal.portal_types
        # Convert to old-school FTI
        migrateFTI(self.portal, 'Plone Site', None,
                   'Factory-based Type Information')
        self.assertEqual(getattr(ttool, 'Plone Site').meta_type,
                         'Factory-based Type Information')
        # Set old style PropertyManaged default page/layout
        self.portal._selected_default_page = 'blah'
        # Convert back
        convertPloneFTIToCMFDynamicViewFTI(self.portal, [])
        # Make sure content exists
        _createObjectByType('Document', self.portal, 'blah')
        # check layout transfer
        self.assertEqual(self.portal.getDefaultPage(), 'blah')
        self.assertEqual(self.portal.getAvailableLayouts(),
                         [('folder_listing', 'Standard view'),
                          ('news_listing', 'News')])
        self.assertEqual(self.portal.getLayout(), 'folder_listing')

    def testConvertPloneFTIToCMFDynamicViewFTITwice(self):
        ttool = self.portal.portal_types
        # Convert to old-school FTI
        migrateFTI(self.portal, 'Plone Site', None,
                   'Factory-based Type Information')
        # Convert back
        convertPloneFTIToCMFDynamicViewFTI(self.portal, [])
        convertPloneFTIToCMFDynamicViewFTI(self.portal, [])
        self.assertEqual(self.portal.getTypeInfo().meta_type,
                        'Factory-based Type Information with dynamic views')

    def testConvertPloneFTIToCMFDynamicViewFTINoFTI(self):
        self.portal.portal_types._delObject('Plone Site')
        # Convert back
        convertPloneFTIToCMFDynamicViewFTI(self.portal, [])

    def testConvertPloneFTIToCMFDynamicViewFTINoTool(self):
        self.portal._delObject('portal_types')
        # Convert back
        convertPloneFTIToCMFDynamicViewFTI(self.portal, [])

    def testAddMethodAliasesForPloneSite(self):
        # Should add method aliases to the Plone Site FTI
        expected_aliases = {
                '(Default)'  : '(dynamic view)',
                'view'       : '(selected layout)',
                'index.html' : '(dynamic view)',
                'edit'       : 'folder_edit_form',
                'sharing'    : 'folder_localrole_form',
              }
        fti = self.portal.getTypeInfo()
        fti.setMethodAliases({})
        addMethodAliasesForPloneSite(self.portal, [])
        fti = self.portal.getTypeInfo()
        aliases = fti.getMethodAliases()
        self.assertEqual(aliases, expected_aliases)

    def testAddMethodAliasesForPloneSiteTwice(self):
        # Should not fail if done twice
        expected_aliases = {
                '(Default)'  : '(dynamic view)',
                'view'       : '(selected layout)',
                'index.html' : '(dynamic view)',
                'edit'       : 'folder_edit_form',
                'sharing'    : 'folder_localrole_form',
              }
        fti = self.portal.getTypeInfo()
        fti.setMethodAliases({})
        addMethodAliasesForPloneSite(self.portal, [])
        addMethodAliasesForPloneSite(self.portal, [])
        fti = self.portal.getTypeInfo()
        aliases = fti.getMethodAliases()
        self.assertEqual(aliases, expected_aliases)

    def testAddMethodAliasesForPloneSiteNoFTI(self):
        # Should not fail FTI is missing
        self.portal.portal_types._delObject('Plone Site')
        addMethodAliasesForPloneSite(self.portal, [])

    def testAddMethodAliasesForPloneSiteNoTool(self):
        # Should not fail tool is missing
        self.portal._delObject('portal_types')
        addMethodAliasesForPloneSite(self.portal, [])

    def testUpdateParentMetaTypesNotToQuery(self):
        # Adds missing property and sets proper default value
        ntp = self.properties.navtree_properties
        self.removeNavTreeProperty('parentMetaTypesNotToQuery')
        self.failIf(ntp.hasProperty('parentMetaTypesNotToQuery'))
        updateParentMetaTypesNotToQuery(self.portal, [])
        self.assertEqual(ntp.getProperty('parentMetaTypesNotToQuery'),
                                    ('Large Plone Folder',))

    def testUpdateParentMetaTypesNotToQueryDoesNotErase(self):
        # Adds missing property and sets proper default value
        ntp = self.properties.navtree_properties
        ntp.manage_changeProperties(parentMetaTypesNotToQuery=('Document', 'Folder'))
        updateParentMetaTypesNotToQuery(self.portal, [])
        self.assertEqual(ntp.getProperty('parentMetaTypesNotToQuery'),
                                    ('Document', 'Folder', 'Large Plone Folder'))

    def testUpdateParentMetaTypesNotToQueryTwice(self):
        # Should not duplcate the value if run twice
        ntp = self.properties.navtree_properties
        self.removeNavTreeProperty('parentMetaTypesNotToQuery')
        updateParentMetaTypesNotToQuery(self.portal, [])
        updateParentMetaTypesNotToQuery(self.portal, [])
        self.assertEqual(ntp.getProperty('parentMetaTypesNotToQuery'),
                                    ('Large Plone Folder',))

    def testUpdateParentMetaTypesNotToQueryNoSheet(self):
        # Should not fail if the prop sheet is missing
        self.properties._delObject('navtree_properties')
        updateParentMetaTypesNotToQuery(self.portal, [])

    def testUpdateParentMetaTypesNotToQueryNoTool(self):
        # Should not fail if the tool is missing
        self.portal._delObject('portal_properties')
        updateParentMetaTypesNotToQuery(self.portal, [])

    def testFixCutActionPermission(self):
        editActions = ('cut',)
        for a in editActions:
            self.removeActionFromTool(a)
        fixCutActionPermission(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixCutActionPermissionTwice(self):
        editActions = ('cut',)
        for a in editActions:
            self.removeActionFromTool(a)
        fixCutActionPermission(self.portal, [])
        fixCutActionPermission(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixCutActionPermissionNoTool(self):
        self.portal._delObject('portal_actions')
        fixCutActionPermission(self.portal, [])

    def testFixExtEditAction(self):
        editActions = ('extedit',)
        for a in editActions:
            self.removeActionFromTool(a)
        fixExtEditAction(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixExtEditActionTwice(self):
        editActions = ('extedit',)
        for a in editActions:
            self.removeActionFromTool(a)
        fixExtEditAction(self.portal, [])
        fixExtEditAction(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testFixExtEditActionNoTool(self):
        self.portal._delObject('portal_actions')
        fixExtEditAction(self.portal, [])

    def testChangeMemberdataExtEditor(self):
        # Should add the ext_editor property
        self.removeMemberdataProperty('ext_editor')
        self.failIf(self.portal_memberdata.hasProperty('ext_editor'))
        changeMemberdataExtEditor(self.portal, [])
        self.assertEqual(self.portal_memberdata.getProperty('ext_editor'), 0)

    def testChangeMemberdataExtEditorExists(self):
        # Should alter existing ext_editor property
        self.portal_memberdata.manage_changeProperties(ext_editor=1)
        changeMemberdataExtEditor(self.portal, [])
        self.assertEqual(self.portal_memberdata.getProperty('ext_editor'), 0)

    def testChangeMemberdataExtEditorTwice(self):
        # Should not fail if migrated again
        self.removeMemberdataProperty('ext_editor')
        self.failIf(self.portal_memberdata.hasProperty('ext_editor'))
        changeMemberdataExtEditor(self.portal, [])
        changeMemberdataExtEditor(self.portal, [])
        self.assertEqual(self.portal_memberdata.getProperty('ext_editor'), 0)

    def testChangeMemberdataExtEditor(self):
        # Should not fail if portal_memberdata is missing
        self.portal._delObject('portal_memberdata')
        changeMemberdataExtEditor(self.portal, [])

    def testFixWorkflowStateTitles(self):
        wfs = ('plone_workflow','folder_workflow')
        wftool = self.portal.portal_workflow
        for wfid in wfs:
            wf = getattr(wftool, wfid)
            for state in wf.states.objectValues():
                state.setProperties(title='junk')
                self.assertEqual(state.title, 'junk')

        fixWorkflowStateTitles(self.portal, [])
        self.assertEqual(wftool.plone_workflow.states.visible.title,
                            'Public Draft')
        self.assertEqual(wftool.folder_workflow.states.visible.title,
                            'Public Draft')

    def testFixWorkflowStateTitlesTwice(self):
        wfs = ('plone_workflow','folder_workflow')
        wftool = self.portal.portal_workflow
        for wfid in wfs:
            wf = getattr(wftool, wfid)
            for state in wf.states.objectValues():
                state.setProperties(title='junk')
                self.assertEqual(state.title, 'junk')

        fixWorkflowStateTitles(self.portal, [])
        fixWorkflowStateTitles(self.portal, [])
        self.assertEqual(wftool.plone_workflow.states.visible.title,
                            'Public Draft')
        self.assertEqual(wftool.folder_workflow.states.visible.title,
                            'Public Draft')

    def testFixWorkflowStateTitlesNoState(self):
        self.portal.portal_workflow.plone_workflow.states._delObject('published')
        fixWorkflowStateTitles(self.portal, [])

    def testFixWorkflowStateTitlesNoStates(self):
        self.portal.portal_workflow.plone_workflow._delObject('states')
        fixWorkflowStateTitles(self.portal, [])

    def testFixWorkflowStateTitlesNoWF(self):
        self.portal.portal_workflow._delObject('plone_workflow')
        fixWorkflowStateTitles(self.portal, [])

    def testFixWorkflowStateTitlesNoTool(self):
        self.portal._delObject('portal_workflow')
        fixWorkflowStateTitles(self.portal, [])

    def testChangeSiteActions(self):
        # Remove some actions, add some others, and change the category of
        # plone_setup
        removeActions = ('small_text', 'normal_text', 'large_text')
        editActions = ('plone_setup','accessibility','contact')
        for a in removeActions:
            self.addActionToTool(a,'site_actions')
        for a in editActions:
            self.removeActionFromTool(a)
        changeSiteActions(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)
        for a in removeActions:
            self.failIf(a in actions)

    def testChangeSiteActionsChangesCategory(self):
        # Existing actions should be removed and recategorized
        editActions = ('plone_setup','accessibility','contact')
        for a in editActions:
            self.removeActionFromTool(a)
            self.addActionToTool(a, 'user')
        changeSiteActions(self.portal, [])
        actions = [x for x in self.actions.listActions() if x.id in editActions]
        # No duplicates
        self.assertEqual(len(actions), len(editActions))
        for a in actions:
            self.assertEqual(a.category, 'site_actions')

    def testChangeSiteActionsTwice(self):
        # Should not fail or duplicate if performed twice
        removeActions = ('small_text', 'normal_text', 'large_text')
        editActions = ('plone_setup','accessibility','contact')
        for a in removeActions:
            self.addActionToTool(a,'site_actions')
        for a in editActions:
            self.removeActionFromTool(a)
            self.addActionToTool(a, 'user')
        changeSiteActions(self.portal, [])
        changeSiteActions(self.portal, [])
        actions = [x for x in self.actions.listActions() if x.id in editActions]
        # No duplicates
        self.assertEqual(len(actions), len(editActions))
        for a in actions:
            self.assertEqual(a.category, 'site_actions')

    def testChangeSiteActionsNoTool(self):
        # Should not fail if the tool is missing
        self.portal._delObject('portal_actions')
        changeSiteActions(self.portal, [])

    def testRemovePloneSetupActionFromPortalMembership(self):
        # Should remove the plone_setup action from the membership_tool
        removeActions = ('plone_setup', )
        for a in removeActions:
            self.addActionToTool(a,'site_actions', 'portal_membership')
        removePloneSetupActionFromPortalMembership(self.portal, [])
        actions = [x for x in self.portal.portal_membership.listActions()]
        for a in removeActions:
            self.failIf(a in actions)

    def testRemovePloneSetupActionFromPortalMembershipTwice(self):
        # Should not fail if performed twice
        removeActions = ('plone_setup', )
        for a in removeActions:
            self.addActionToTool(a,'site_actions', 'portal_membership')
        removePloneSetupActionFromPortalMembership(self.portal, [])
        removePloneSetupActionFromPortalMembership(self.portal, [])
        actions = [x for x in self.portal.portal_membership.listActions()]
        for a in removeActions:
            self.failIf(a in actions)

    def testRemovePloneSetupActionFromPortalMembershipNoAction(self):
        # Should not fail if action is missing
        removeActions = ('plone_setup', )
        removePloneSetupActionFromPortalMembership(self.portal, [])
        actions = [x for x in self.portal.portal_membership.listActions()]
        for a in removeActions:
            self.failIf(a in actions)

    def testRemovePloneSetupActionFromPortalMembershipNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_membership')
        removePloneSetupActionFromPortalMembership(self.portal, [])

    def testFixViewMethodAliases(self):
        # Should set 'view' alias for core types and Plone Site to (selected layout)
        types = ('Document', 'Event', 'Favorite', 'File', 'Folder', 'Image', 'Link', 'News Item', 'Topic', 'Plone Site')
        ttool = self.portal.portal_types

        for typeName in types:
            fti = getattr(ttool, typeName)
            aliases = fti.getMethodAliases()
            aliases['view'] = '(dynamic view)'
            fti.setMethodAliases(aliases)

        fixViewMethodAliases(self.portal, [])

        for typeName in types:
            fti = getattr(ttool, typeName)
            aliases = fti.getMethodAliases()
            self.assertEqual(aliases['view'], '(selected layout)', typeName)


    def testFixViewMethodAliasesTwice(self):
        # Should not fail if called twice
        types = ('Document', 'Event', 'Favorite', 'File', 'Folder', 'Image', 'Link', 'News Item', 'Topic', 'Plone Site')
        ttool = self.portal.portal_types

        for typeName in types:
            fti = getattr(ttool, typeName)
            aliases = fti.getMethodAliases()
            aliases['view'] = '(dynamic view)'
            fti.setMethodAliases(aliases)

        fixViewMethodAliases(self.portal, [])
        fixViewMethodAliases(self.portal, [])

        for typeName in types:
            fti = getattr(ttool, typeName)
            aliases = fti.getMethodAliases()
            self.assertEqual(aliases['view'], '(selected layout)')

    def testFixViewMethodAliasesNoFTI(self):
        # Should not fail if there is no FTI, but convert rest
        types = ('Event', 'Favorite', 'File', 'Folder', 'Image', 'Link', 'News Item', 'Topic', 'Plone Site')
        ttool = self.portal.portal_types
        ttool._delObject('Document')

        for typeName in types:
            fti = getattr(ttool, typeName)
            aliases = fti.getMethodAliases()
            aliases['view'] = '(dynamic view)'
            fti.setMethodAliases(aliases)

        fixViewMethodAliases(self.portal, [])

        for typeName in types:
            fti = getattr(ttool, typeName)
            aliases = fti.getMethodAliases()
            self.assertEqual(aliases['view'], '(selected layout)')

    def testFixViewMethodAliasesNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_types')
        fixViewMethodAliases(self.portal, [])

    def testFixPortalEditAndSharingActions(self):
        # Portal should use /edit and /sharing for edit and sharing actions
        fti = self.portal.getTypeInfo()
        for action in fti.listActions():
            if action.getId() == 'edit':
                action.setActionExpression('string:${object_url}/folder_edit_form')
            elif action.getId() == 'local_roles':
                action.setActionExpression('string:${object_url}/folder_localrole_form')
        fixPortalEditAndSharingActions(self.portal, [])
        for action in fti.listActions():
            if action.getId() == 'edit':
                self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')
            elif action.getId() == 'local_roles':
                self.assertEqual(action.getActionExpression(), 'string:${object_url}/sharing')

    def testFixPortalEditAndSharingActionsTwice(self):
        # Portal should use /edit and /sharing for edit and sharing actions
        fti = self.portal.getTypeInfo()
        for action in fti.listActions():
            if action.getId() == 'edit':
                action.setActionExpression('string:${object_url}/folder_edit_form')
            elif action.getId() == 'local_roles':
                action.setActionExpression('string:${object_url}/folder_localrole_form')
        fixPortalEditAndSharingActions(self.portal, [])
        fixPortalEditAndSharingActions(self.portal, [])
        for action in fti.listActions():
            if action.getId() == 'edit':
                self.assertEqual(action.getActionExpression(), 'string:${object_url}/edit')
            elif action.getId() == 'local_roles':
                self.assertEqual(action.getActionExpression(), 'string:${object_url}/sharing')

    def testFixPortalEditAndSharingActionsNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_types')
        fixPortalEditAndSharingActions(self.portal, [])

    def testFixPortalEditAndSharingActionsNoFTI(self):
        # Should not fail if FTI is missing
        self.portal.portal_types._delObject('Plone Site')
        fixPortalEditAndSharingActions(self.portal, [])

    def testHasCMFUidTools(self):
        portal_ids = self.portal.objectIds()
        tool_ids = ('portal_uidgenerator', 'portal_uidannotation',
                   'portal_uidhandler')
        for id in tool_ids:
            self.failUnless(id in portal_ids, id)

    def testaddCMFUidTools(self):
        tool_ids = ('portal_uidgenerator', 'portal_uidannotation',
                   'portal_uidhandler')
        # remove tools
        self.setRoles(('Manager',))
        self.portal.manage_delObjects(list(tool_ids))
        for id in tool_ids:
            self.failIf(id in self.portal.objectIds(), id)
        # add tools
        addCMFUidTools(self.portal, [])
        for id in tool_ids:
            self.failUnless(id in self.portal.objectIds(), id)
            tool = getattr(self.portal, id)
            self.failUnless(tool.title) # has it a title?
        # a second add shouldn't break
        addCMFUidTools(self.portal, [])

    def testfixCSSMediaTypes(self):
        cssmediatypes = [
            ('member.css', 'screen'),
            ('RTL.css', 'screen'),
            ('presentation.css', 'projection'),
            ('ploneCustom.css', 'all'),
        ]
        cssreg = getattr(self.portal, 'portal_css')
        stylesheet_ids = cssreg.getResourceIds()
        #correct the media types
        fixCSSMediaTypes(self.portal, [])
        #check if the media types are set correctly
        for stylesheet,cssmediatype in cssmediatypes:
            if stylesheet in stylesheet_ids:
                cssresource=cssreg.getResource(stylesheet)
                self.assertEqual(cssresource.getMedia(),cssmediatype)
        # a second add shouldn't break
        fixCSSMediaTypes(self.portal, [])

    def testAddWFStateFilteringToNavTree(self):
        # Should add new navtree_properties
        self.removeNavTreeProperty('enable_wf_state_filtering')
        self.removeNavTreeProperty('wf_states_to_show')
        self.failIf(self.properties.navtree_properties.hasProperty('enable_wf_state_filtering'))
        addWFStateFilteringToNavTree(self.portal, [])
        self.failUnless(self.properties.navtree_properties.hasProperty('enable_wf_state_filtering'))
        self.failUnless(self.properties.navtree_properties.hasProperty('wf_states_to_show'))

    def testAddWFStateFilteringToNavTreeTwice(self):
        # Should not fail if migrated again
        self.removeNavTreeProperty('enable_wf_state_filtering')
        self.removeNavTreeProperty('wf_states_to_show')
        self.failIf(self.properties.navtree_properties.hasProperty('enable_wf_state_filtering'))
        addWFStateFilteringToNavTree(self.portal, [])
        addWFStateFilteringToNavTree(self.portal, [])
        self.failUnless(self.properties.navtree_properties.hasProperty('enable_wf_state_filtering'))
        self.failUnless(self.properties.navtree_properties.hasProperty('wf_states_to_show'))

    def testAddWFStateFilteringToNavTreeNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addWFStateFilteringToNavTree(self.portal, [])

    def testAddWFStateFilteringToNavTreeNoSheet(self):
        # Should not fail if navtree_properties is missing
        self.properties._delObject('navtree_properties')
        addWFStateFilteringToNavTree(self.portal, [])


    def testAddIconForNavigationSettingsConfiglet(self):
        # Should add the full_screen action icon
        self.removeActionIconFromTool('NavigationSettings')
        addIconForNavigationSettingsConfiglet(self.portal, [])
        self.failUnless('NavigationSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForNavigationSettingsConfigletTwice(self):
        # Should not fail if migrated again
        self.removeActionIconFromTool('NavigationSettings')
        addIconForNavigationSettingsConfiglet(self.portal, [])
        addIconForNavigationSettingsConfiglet(self.portal, [])
        self.failUnless('NavigationSettings' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddIconForNavigationSettingsConfigletNoTool(self):
        # Should not fail if portal_actionicons is missing
        self.portal._delObject('portal_actionicons')
        addIconForNavigationSettingsConfiglet(self.portal, [])

    def testAddSearchAndNavigationConfiglets(self):
        # Should add the full_screen action icon
        self.removeActionFromTool('NavigationSettings', action_provider='portal_controlpanel')
        self.removeActionFromTool('SearchSettings', action_provider='portal_controlpanel')
        addSearchAndNavigationConfiglets(self.portal, [])
        self.failUnless('NavigationSettings' in [x.getId() for x in self.cp.listActions()])
        self.failUnless('SearchSettings' in [x.getId() for x in self.cp.listActions()])

    def testAddSearchAndNavigationConfigletsTwice(self):
        # Should not fail if done twice
        self.removeActionFromTool('NavigationSettings', action_provider='portal_controlpanel')
        self.removeActionFromTool('SearchSettings', action_provider='portal_controlpanel')
        addSearchAndNavigationConfiglets(self.portal, [])
        addSearchAndNavigationConfiglets(self.portal, [])
        self.failUnless('NavigationSettings' in [x.getId() for x in self.cp.listActions()])
        self.failUnless('SearchSettings' in [x.getId() for x in self.cp.listActions()])

    def testAddSearchAndNavigationConfigletsNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_controlpanel')
        addSearchAndNavigationConfiglets(self.portal, [])

    def testSendtoActionAllowSendtoPermission(self):
        atool = self.portal.portal_actions
        for action in atool._cloneActions():
            if action.getId() == "sendto":
                self.failUnlessEqual(action.permissions,
                                     (AllowSendto,))

    def testSendtoActionAllowSendtoPermissionNA(self):
        atool = self.portal.portal_actions
        # should not break if action is not available
        atool._actions = ()
        setupAllowSendtoPermission(self.portal, [])
        # should not break if tool is missing
        self.portal._delObject('portal_actions')
        setupAllowSendtoPermission(self.portal, [])

    def testReaddVisibleIdsMemberProperty(self):
        # Should add the visible_ids property
        self.removeMemberdataProperty('visible_ids')
        self.failIf(self.portal.portal_memberdata.hasProperty('visible_ids'))
        readdVisibleIdsMemberProperty(self.portal, [])
        self.failUnless(self.portal.portal_memberdata.hasProperty('visible_ids'))

    def testReaddVisibleIdsMemberPropertyTwice(self):
        # Should not fail if migrated again
        self.removeMemberdataProperty('visible_ids')
        self.failIf(self.portal.portal_memberdata.hasProperty('visible_ids'))
        readdVisibleIdsMemberProperty(self.portal, [])
        readdVisibleIdsMemberProperty(self.portal, [])
        self.failUnless(self.portal.portal_memberdata.hasProperty('visible_ids'))

    def testReaddVisibleIdsMemberPropertyNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_memberdata')
        readdVisibleIdsMemberProperty(self.portal, [])

    def testAddCMFTypesToSearchBlackList(self):
        # Should add CMF types to the types_not_searched property
        self.removeSiteProperty('types_not_searched')
        self.failIf(self.properties.site_properties.hasProperty('types_not_searched'))
        addCMFTypesToSearchBlackList(self.portal, [])
        self.failUnless(self.properties.site_properties.hasProperty('types_not_searched'))
        self.failUnless('CMF Document' in self.properties.site_properties.getProperty('types_not_searched'))

    def testAddCMFTypesToSearchBlackListTwice(self):
        # Should not fail if migrated again
        self.removeSiteProperty('types_not_searched')
        self.failIf(self.properties.site_properties.hasProperty('types_not_searched'))
        addCMFTypesToSearchBlackList(self.portal, [])
        list_len = len(self.properties.site_properties.getProperty('types_not_searched'))
        addCMFTypesToSearchBlackList(self.portal, [])
        list_len2 = len(self.properties.site_properties.getProperty('types_not_searched'))
        self.assertEqual(list_len2, list_len)

    def testAddCMFTypesToSearchBlackListPreservesChanges(self):
        # Should preserve existing values
        self.properties.site_properties.manage_changeProperties(types_not_searched=
                                            ['test type'])
        addCMFTypesToSearchBlackList(self.portal, [])
        self.failUnless('CMF Document' in self.properties.site_properties.getProperty('types_not_searched'))
        self.failUnless('test type' in self.properties.site_properties.getProperty('types_not_searched'))


    def testAddCMFTypesToSearchBlackListNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        addCMFTypesToSearchBlackList(self.portal, [])

    def testAddCMFTypesToSearchBlackListNoSheet(self):
        # Should not fail if site_properties is missing
        self.properties._delObject('site_properties')
        addCMFTypesToSearchBlackList(self.portal, [])

    def testConvertDefaultPageTypesToWhitelist(self):
        # Should add the default_page_types property and remove the
        # non_default_page_types property
        self.addSiteProperty('non_default_page_types')
        self.removeSiteProperty('default_page_types')
        self.failIf(self.properties.site_properties.hasProperty('default_page_types'))
        self.failUnless(self.properties.site_properties.hasProperty('non_default_page_types'))
        convertDefaultPageTypesToWhitelist(self.portal, [])
        self.failIf(self.properties.site_properties.hasProperty('non_default_page_types'))
        self.failUnless(self.properties.site_properties.hasProperty('default_page_types'))

    def testConvertDefaultPageTypesToWhitelistTwice(self):
        # Should not fail if migrated again
        self.addSiteProperty('non_default_page_types')
        self.removeSiteProperty('default_page_types')
        convertDefaultPageTypesToWhitelist(self.portal, [])
        convertDefaultPageTypesToWhitelist(self.portal, [])
        self.failIf(self.properties.site_properties.hasProperty('non_default_page_types'))
        self.failUnless(self.properties.site_properties.hasProperty('default_page_types'))

    def testConvertDefaultPageTypesToWhitelistNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_properties')
        convertDefaultPageTypesToWhitelist(self.portal, [])

    def testConvertDefaultPageTypesToWhitelistNoSheet(self):
        # Should not fail if site_properties is missing
        self.properties._delObject('site_properties')
        convertDefaultPageTypesToWhitelist(self.portal, [])

    def testChangeAvailableViewsForFolders(self):
        # Should add a list of view template to the various folderish types
        # tests on Topic
        types = self.portal.portal_types
        types.Topic.manage_changeProperties(view_methods=['atct_topic_view'])
        self.assertEqual(types.Topic.view_methods, ('atct_topic_view',))
        changeAvailableViewsForFolders(self.portal, [])
        self.failUnless('atct_album_view' in types.Topic.getAvailableViewMethods(None))

    def testChangeAvailableViewsForFoldersTwice(self):
        # Should not fail if migrated again (test of Folder this time
        types = self.portal.portal_types
        types.Folder.manage_changeProperties(view_methods=['folder_listing'])
        self.assertEqual(types.Folder.view_methods, ('folder_listing',))
        changeAvailableViewsForFolders(self.portal, [])
        changeAvailableViewsForFolders(self.portal, [])
        self.failUnless('atct_album_view' in types.Folder.getAvailableViewMethods(None))

    def testChangeAvailableViewsForFoldersNoTool(self):
        # Should not fail if portal_properties is missing
        self.portal._delObject('portal_types')
        changeAvailableViewsForFolders(self.portal, [])

    def testChangeAvailableViewsForFoldersNoFTI(self):
        # Should not fail if site_properties is missing
        self.portal.portal_types._delObject('Topic')
        changeAvailableViewsForFolders(self.portal, [])

    def testEnableSyndicationOnTopics(self):
        # Test that we enable syndication on all existing topics
        syn = self.portal.portal_syndication
        news = self.portal.news
        events = self.portal.events
        # Only owners and managers can set syndication properties
        self.setRoles(['Manager'])
        syn.disableSyndication(news)
        syn.disableSyndication(events)
        self.failIf(syn.isSyndicationAllowed(news))
        self.failIf(syn.isSyndicationAllowed(events))
        enableSyndicationOnTopics(self.portal,[])
        self.failUnless(syn.isSyndicationAllowed(news))
        self.failUnless(syn.isSyndicationAllowed(events))
        self.failUnless(syn.isSiteSyndicationAllowed())

    def testEnableSyndicationOnTopicsTwice(self):
        # Should not fail if migrated again
        syn = self.portal.portal_syndication
        news = self.portal.news
        events = self.portal.events
        self.setRoles(['Manager'])
        syn.disableSyndication(news)
        syn.disableSyndication(events)
        enableSyndicationOnTopics(self.portal,[])
        enableSyndicationOnTopics(self.portal,[])
        self.failUnless(syn.isSyndicationAllowed(news))
        self.failUnless(syn.isSyndicationAllowed(events))

    def testEnableSyndicationOnTopicsWithSiteSyndicationDisabled(self):
        # Should preserve site syndication state but still enable
        syn = self.portal.portal_syndication
        news = self.portal.news
        events = self.portal.events
        self.setRoles(['Manager'])
        syn.disableSyndication(news)
        syn.disableSyndication(events)
        syn.editProperties(isAllowed=False)
        self.failIf(syn.isSiteSyndicationAllowed())
        enableSyndicationOnTopics(self.portal,[])
        self.failIf(syn.isSiteSyndicationAllowed())
        syn.editProperties(isAllowed=True)
        self.failUnless(syn.isSyndicationAllowed(news))

    def testEnableSyndicationOnTopicsNoTool(self):
        # Should not fail if portal_syndication is missing
        self.portal._delObject('portal_syndication')
        enableSyndicationOnTopics(self.portal,[])

    def testEnableSyndicationOnTopicsNoCatalog(self):
        # Should not fail if portal_catalog is missing
        self.portal._delObject('portal_catalog')
        enableSyndicationOnTopics(self.portal,[])

    def testDisableSyndicationAction(self):
        # Should disable the syndication
        syn = self.portal.portal_syndication
        new_actions = syn._cloneActions()
        for action in new_actions:
            if action.getId() == 'syndication':
                action.visible = True
        syn._actions = new_actions
        disableSyndicationAction(self.portal, [])
        actions = syn.listActions()
        syn_actions = [x for x in actions if x.id == 'syndication']
        self.assertEqual(len(syn_actions), 1)
        self.failIf(syn_actions[0].visible)

    def testDisableSyndicationActionTwice(self):
        # Should not fail if migrated twice
        syn = self.portal.portal_syndication
        new_actions = syn._cloneActions()
        for action in new_actions:
            if action.getId() == 'syndication':
                action.visible = True
        syn._actions = new_actions
        disableSyndicationAction(self.portal, [])
        disableSyndicationAction(self.portal, [])
        actions = syn.listActions()
        syn_actions = [x for x in actions if x.id == 'syndication']
        self.assertEqual(len(syn_actions), 1)
        self.failIf(syn_actions[0].visible)

    def testDisableSyndicationActionNoAction(self):
        # Should not fail if the action is already gone
        self.removeActionFromTool('syndication',
                                        action_provider='portal_syndication')
        disableSyndicationAction(self.portal, [])

    def testDisableSyndicationActionNoTool(self):
        # Should not fail if portal_syndication is missing
        self.portal._delObject('portal_syndication')
        disableSyndicationAction(self.portal, [])

    def testAlterRSSActionTitleAction(self):
        # Should change the RSS action title
        new_actions = self.actions._cloneActions()
        for action in new_actions:
            if action.getId() == 'rss':
                action.title = 'A bad title with contents in it'
        self.actions._actions = new_actions
        alterRSSActionTitle(self.portal, [])
        actions = self.actions.listActions()
        rss_actions = [x for x in actions if x.id == 'rss']
        self.assertEqual(len(rss_actions), 1)
        self.failUnless(rss_actions[0].title == 'RSS feed of this listing')

    def testAlterRSSActionTitleTwice(self):
        # Should not fail if migrated twice
        new_actions = self.actions._cloneActions()
        for action in new_actions:
            if action.getId() == 'rss':
                action.title = 'A bad title with contents in it'
        self.actions._actions = new_actions
        alterRSSActionTitle(self.portal, [])
        alterRSSActionTitle(self.portal, [])
        actions = self.actions.listActions()
        rss_actions = [x for x in actions if x.id == 'rss']
        self.assertEqual(len(rss_actions), 1)
        self.failUnless(rss_actions[0].title == 'RSS feed of this listing')

    def testAlterRSSActionTitleNoAction(self):
        # Should not fail if the action is already gone
        self.removeActionFromTool('rss')
        alterRSSActionTitle(self.portal, [])

    def testAlterRSSActionTitleNoTool(self):
        # Should not fail if portal_actions is missing
        self.portal._delObject('portal_actions')
        alterRSSActionTitle(self.portal, [])

    def testAddPastEventsTopic(self):
        #Should add a subtopic to the events_topic for past events
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        events_topic = self.portal.events.events_topic
        self.failIf('previous' in events_topic.objectIds())
        addPastEventsTopic(self.portal, [])
        self.failUnless('previous' in events_topic.objectIds())
        topic = getattr(events_topic.aq_base, 'previous')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')

    def testAddPastEventsTopicTwice(self):
        #Should not fail if done twice
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        events_topic = self.portal.events.events_topic
        self.failIf('previous' in events_topic.objectIds())
        addPastEventsTopic(self.portal, [])
        addPastEventsTopic(self.portal, [])
        self.failUnless('previous' in events_topic.objectIds())
        topic = getattr(events_topic.aq_base, 'previous')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')

    def testAddPastEventsTopicNoATCT(self):
        #Should not do anything unless ATCT is installed
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        events_topic = self.portal.events.events_topic
        self.portal._delObject('portal_atct')
        addPastEventsTopic(self.portal, [])
        self.failUnless('previous' not in events_topic.objectIds())

    def testAddPastEventsTopicNoEvents(self):
        #Should not do anything unless the events folder exists
        self.portal._delObject('events')
        addPastEventsTopic(self.portal, [])

    def testAddPastEventsTopicNoParent(self):
        #Should not do anything unless the events_topic exists
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        addPastEventsTopic(self.portal, [])

    def testAddDateCriterionToEventsTopicTopic(self):
        #Should add a date crierion to events topic to limit to future events
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        events_topic = self.portal.events.events_topic
        self.failIf('crit__start_ATFriendlyDateCriteria' in events_topic.objectIds())
        addDateCriterionToEventsTopic(self.portal, [])
        self.failUnless('crit__start_ATFriendlyDateCriteria' in events_topic.objectIds())

    def testAddDateCriterionToEventsTopicTwice(self):
        #Should not fail if done twice
        self.portal._delObject('events')
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        events_topic = self.portal.events.events_topic
        self.failIf('crit__start_ATFriendlyDateCriteria' in events_topic.objectIds())
        addDateCriterionToEventsTopic(self.portal, [])
        addDateCriterionToEventsTopic(self.portal, [])
        self.failUnless('crit__start_ATFriendlyDateCriteria' in events_topic.objectIds())

    def testAddDateCriterionToEventsTopicNoATCT(self):
        #Should not fail if ATCT is not installed
        self.portal._delObject('portal_atct')
        addDateCriterionToEventsTopic(self.portal, [])

    def testFixDuplicatePortalRootSharingAction(self):
        # Portal should use 'local_roles' as id of sharing action
        fti = self.portal.getTypeInfo()
        idx = 0
        oldAction = None
        for action in fti.listActions():
            if action.getId() == 'local_roles':
                oldAction = action
                break
            idx += 1
        fti.deleteActions((idx,))
        fti.addAction('sharing',
                        name=oldAction.Title(),
                        action=oldAction.getActionExpression(),
                        condition=oldAction.getCondition(),
                        permission=oldAction.getPermissions(),
                        category=oldAction.getCategory(),
                        visible=oldAction.getVisibility())

        fixDuplicatePortalRootSharingAction(self.portal, [])

        haveSharing = False
        haveLocalRoles = False
        for a in fti.listActions():
            if a.getId() == 'sharing':
                haveSharing = True
            elif a.getId() == 'local_roles':
                haveLocalRoles = True
        self.failIf(haveSharing)
        self.failUnless(haveLocalRoles)

    def testFixDuplicatePortalRootSharingActionTwice(self):
        # Should not fail if called twice
        fti = self.portal.getTypeInfo()
        idx = 0
        oldAction = None
        for action in fti.listActions():
            if action.getId() == 'local_roles':
                oldAction = action
                break
            idx += 1
        fti.deleteActions((idx,))
        fti.addAction('sharing',
                        name=oldAction.Title(),
                        action=oldAction.getActionExpression(),
                        condition=oldAction.getCondition(),
                        permission=oldAction.getPermissions(),
                        category=oldAction.getCategory(),
                        visible=oldAction.getVisibility())

        fixDuplicatePortalRootSharingAction(self.portal, [])
        fixDuplicatePortalRootSharingAction(self.portal, [])

        haveSharing = False
        haveLocalRoles = False
        for a in fti.listActions():
            if a.getId() == 'sharing':
                haveSharing = True
            elif a.getId() == 'local_roles':
                haveLocalRoles = True
        self.failIf(haveSharing)
        self.failUnless(haveLocalRoles)

    def testFixDuplicatePortalRootSharingActionWithCorrectLocalRolesAction(self):
        # Should not add local_roles again if it already exists

        fti = self.portal.getTypeInfo()
        fti.addAction('sharing',
                        name='Sharing',
                        action='string:${object_url}/sharing',
                        condition='',
                        permission=('Manage properties',),
                        category='object',
                        visible=1)

        fixDuplicatePortalRootSharingAction(self.portal, [])

        haveSharing = False
        haveLocalRoles = False
        haveLocalRolesTwice = False

        for a in fti.listActions():
            if a.getId() == 'sharing':
                haveSharing = True
            elif a.getId() == 'local_roles':
                if haveLocalRoles:
                    haveLocalRolesTwice = True
                haveLocalRoles = True
        self.failIf(haveSharing)
        self.failUnless(haveLocalRoles)
        self.failIf(haveLocalRolesTwice)

    def testFixDuplicatePortalRootSharingActionNoTool(self):
        # Should not fail if tool is missing
        self.portal._delObject('portal_types')
        fixDuplicatePortalRootSharingAction(self.portal, [])

    def testFixDuplicatePortalRootSharingActionNoFTI(self):
        # Should not fail if FTI is missing
        self.portal.portal_types._delObject('Plone Site')
        fixDuplicatePortalRootSharingAction(self.portal, [])

    def testMoveDefaultTopicsToPortalRoot(self):
        # Should move the news and events topics to the portal root
        self.setRoles(['Manager','Member'])
        self.portal.manage_delObjects(['news','events'])
        addNewsFolder(self.portal, [])
        addNewsTopic(self.portal, [])
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        moveDefaultTopicsToPortalRoot(self.portal,[])
        self.assertEqual(self.portal.news.portal_type, 'Topic')
        self.assertEqual(self.portal.events.portal_type, 'Topic')
        self.failIf('site_news' in self.portal.objectIds())

    def testMoveDefaultTopicsToPortalRootTwice(self):
        # Shouldn't fail if migrated twice
        self.setRoles(['Manager','Member'])
        self.portal.manage_delObjects(['news','events'])
        addNewsFolder(self.portal, [])
        addNewsTopic(self.portal, [])
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        # add a news item so that the old_news gets created
        self.setRoles(['Manager', 'Member'])
        self.portal.news.invokeFactory('News Item', 'my_news')
        moveDefaultTopicsToPortalRoot(self.portal,[])
        moveDefaultTopicsToPortalRoot(self.portal,[])
        self.failUnless('old_news' in self.portal.objectIds())
        self.assertEqual(self.portal.news.portal_type, 'Topic')
        self.assertEqual(self.portal.events.portal_type, 'Topic')

    def testMoveDefaultTopicsToPortalRootWithContent(self):
        # Should move the old news folder to site_news if there are any items in it
        self.setRoles(['Manager','Member'])
        self.portal.manage_delObjects(['news','events'])
        addNewsFolder(self.portal, [])
        addNewsTopic(self.portal, [])
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        # Add news to folder
        self.portal.news.invokeFactory('News Item', 'news1')
        moveDefaultTopicsToPortalRoot(self.portal,[])
        self.assertEqual(self.portal.news.portal_type, 'Topic')
        self.assertEqual(self.portal.events.portal_type, 'Topic')
        self.failUnless('old_news' in self.portal.objectIds())
        self.assertEqual(self.portal.old_news.portal_type, 'Large Plone Folder')
        # Title changed
        self.assertEqual(self.portal.old_news.Title(), 'Old News')
        # not Excluded from navigation
        # self.failUnless(self.portal.old_news.exclude_from_nav())
        # Sub-objects in place
        self.failUnless('news1' in self.portal.old_news.objectIds())
        self.failIf('old_events' in self.portal.objectIds())

    def testMoveDefaultTopicsToPortalRootPreservesOrder(self):
        # Move should preserve position
        self.setRoles(['Manager','Member'])
        self.portal.manage_delObjects(['news','events'])
        addNewsFolder(self.portal, [])
        addNewsTopic(self.portal, [])
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        self.portal.moveObject('news', 15)
        moveDefaultTopicsToPortalRoot(self.portal,[])
        self.assertEqual(self.portal.news.portal_type, 'Topic')
        self.assertEqual(self.portal.events.portal_type, 'Topic')
        self.assertEqual(self.portal.getObjectPosition('news'), 15)

    def testMoveDefaultTopicsToPortalRootNoTopics(self):
        # Should not fail if topics are missing
        self.setRoles(['Manager','Member'])
        self.portal.manage_delObjects(['news','events'])
        addNewsFolder(self.portal, [])
        addEventsFolder(self.portal, [])
        moveDefaultTopicsToPortalRoot(self.portal,[])

    def testMoveDefaultTopicsToPortalRootNoFolders(self):
        # Should not fail if folders are missing
        self.setRoles(('Manager',))
        self.portal.manage_delObjects(['news','events'])
        moveDefaultTopicsToPortalRoot(self.portal,[])

    def testMoveDefaultTopicsToPortalRootIfTopicIsDisallowedContentType(self):
        # Should move the news and events topics to the portal root
        self.setRoles(['Manager', 'Member'])
        self.portal.manage_delObjects(['news', 'events'])
        addNewsFolder(self.portal, [])
        addNewsTopic(self.portal, [])
        addEventsFolder(self.portal, [])
        addEventsTopic(self.portal, [])
        # Disallow Topic in Plone Site
        fti = self.types['Plone Site']
        fti.manage_changeProperties(filter_content_types=True,
                                    allowed_content_types=('Document',))
        # Move Topics
        moveDefaultTopicsToPortalRoot(self.portal,[])
        self.assertEqual(self.portal.news.portal_type, 'Topic')
        self.assertEqual(self.portal.events.portal_type, 'Topic')

    def testAlterSortCriterionOnNewsTopic(self):
        #Should change sorting on the news topic to use effective
        topic = self.portal.news
        topic.setSortCriterion('created', False)
        self.failUnless('crit__created_ATSortCriterion' in topic.objectIds())
        alterSortCriterionOnNewsTopic(self.portal, [])
        sorter = topic.getSortCriterion()
        self.assertEqual(sorter.Field(), 'effective')
        self.failUnless(sorter.getReversed())

    def testAlterSortCriterionOnNewsTopicTwice(self):
        #Should not fail if done twice
        topic = self.portal.news
        topic.setSortCriterion('created', False)
        alterSortCriterionOnNewsTopic(self.portal, [])
        alterSortCriterionOnNewsTopic(self.portal, [])
        sorter = topic.getSortCriterion()
        self.assertEqual(sorter.Field(), 'effective')
        self.failUnless(sorter.getReversed())

    def testAlterSortCriterionOnNewsTopicNoTopic(self):
        #Should not fail if the topic is missing
        self.portal._delObject('events')
        alterSortCriterionOnNewsTopic(self.portal, [])

    def testAlterSortCriterionOnNewsTopicNoATCT(self):
        #Should not fail if ATCT is not installed
        topic = self.portal.news
        topic.setSortCriterion('created', False)
        self.portal._delObject('portal_atct')
        alterSortCriterionOnNewsTopic(self.portal, [])

    def testFixPreferenceActionTitle(self):
        # Should change the preferences action title
        new_actions = self.membership._cloneActions()
        for action in new_actions:
            if action.getId() == 'preferences':
                action.title = 'My Preferences'
        self.membership._actions = new_actions
        fixPreferenceActionTitle(self.portal, [])
        actions = self.membership.listActions()
        pref_actions = [x for x in actions if x.id == 'preferences']
        self.failUnless(pref_actions[0].title == 'Preferences')

    def testFixPreferenceActionTitleTwice(self):
        # Should not fail if migrated twice
        new_actions = self.membership._cloneActions()
        for action in new_actions:
            if action.getId() == 'preferences':
                action.title = 'My Preferences'
        self.membership._actions = new_actions
        fixPreferenceActionTitle(self.portal, [])
        fixPreferenceActionTitle(self.portal, [])
        actions = self.membership.listActions()
        pref_actions = [x for x in actions if x.id == 'preferences']
        self.failUnless(pref_actions[0].title == 'Preferences')

    def testFixPreferenceActionTitleNoAction(self):
        # Should not fail if the action is already gone
        self.removeActionFromTool('preferences', action_provider='portal_membership')
        fixPreferenceActionTitle(self.portal, [])

    def testFixPreferenceActionTitleNoTool(self):
        # Should not fail if portal_membership is missing
        self.portal._delObject('portal_membership')
        fixPreferenceActionTitle(self.portal, [])

    def testChangeNewsTopicDefaultView(self):
        # Should change the news topic default view to folder_summary_view
        news = self.portal.news
        news.setLayout('folder_listing')
        self.assertEqual(news.getLayout(), 'folder_listing')
        changeNewsTopicDefaultView(self.portal, [])
        self.assertEqual(news.getLayout(), 'folder_summary_view')

    def testChangeNewsTopicDefaultViewTwice(self):
        # Should not fail if migrated twice
        news = self.portal.news
        news.setLayout('folder_listing')
        self.assertEqual(news.getLayout(), 'folder_listing')
        changeNewsTopicDefaultView(self.portal, [])
        changeNewsTopicDefaultView(self.portal, [])
        self.assertEqual(news.getLayout(), 'folder_summary_view')

    def testChangeNewsTopicDefaultViewNoTopic(self):
        # Should not fail if the topic is missing
        self.portal._delObject('news')
        changeNewsTopicDefaultView(self.portal, [])

    def testFixCMFLegacyLayerInDefault(self):
        # Should move cmf_legacy to end of skin path
        self.addSkinLayer('cmf_legacy', pos=0)
        fixCMFLegacyLayer(self.portal, [])
        path = self.skins.getSkinPath('Plone Default')
        self.assertEqual(path[-11:], ',cmf_legacy')

    def testFixCMFLegacyLayerInTableless(self):
        # Should move cmf_legacy to end of skin path
        self.addSkinLayer('cmf_legacy', skin='Plone Tableless', pos=0)
        fixCMFLegacyLayer(self.portal, [])
        path = self.skins.getSkinPath('Plone Tableless')
        self.assertEqual(path[-11:], ',cmf_legacy')

    def testFixCMFLegacyLayerTwice(self):
        # Should not fail if migrated again
        self.addSkinLayer('cmf_legacy', pos=0)
        fixCMFLegacyLayer(self.portal, [])
        fixCMFLegacyLayer(self.portal, [])
        path = self.skins.getSkinPath('Plone Default')
        self.assertEqual(path[-11:], ',cmf_legacy')

    def testFixCMFLegacyLayerNoTool(self):
        # Should not fail if skins tool is missing
        self.portal._delObject('portal_skins')
        fixCMFLegacyLayer(self.portal, [])

    def testFixCMFLegacyLayerNoLayer(self):
        # Should not fail if cmf_legacy layer is missing
        self.removeSkinLayer('cmf_legacy')
        fixCMFLegacyLayer(self.portal, [])
        # The missing layer is *not* added by the migration
        path = self.skins.getSkinPath('Plone Default')
        self.failIf('cmf_legacy' in path)

    def testReorderObjectButtons(self):
        # Should reorder the edit-content actions
        editActions = ('rename', 'cut', 'copy', 'paste', 'delete')
        for a in editActions:
            self.removeActionFromTool(a)
        bad_actions = list(editActions)
        bad_actions.reverse()
        for a in bad_actions:
            self.addActionToTool(a, 'object_buttons')
        reorderObjectButtons(self.portal, [])
        actions = [x.id for x in self.actions.listActions() if x.category ==
                                    'object_buttons']
        self.assertEqual(actions, list(editActions))

    def testReorderObjectButtonsTwice(self):
        # Should not fail if performed twice
        editActions = ('rename', 'cut', 'copy', 'paste', 'delete')
        for a in editActions:
            self.removeActionFromTool(a)
        bad_actions = list(editActions)
        bad_actions.reverse()
        for a in bad_actions:
            self.addActionToTool(a, 'object_buttons')
        reorderObjectButtons(self.portal, [])
        reorderObjectButtons(self.portal, [])
        actions = [x.id for x in self.actions.listActions() if x.category ==
                                    'object_buttons']
        self.assertEqual(actions, list(editActions))

    def testReorderObjectButtonsNoTool(self):
        # Should not fail if portal_actions is missing
        self.portal._delObject('portal_actions')
        reorderObjectButtons(self.portal, [])

    def testReorderObjectButtonsNoActions(self):
        # Should not fail if the actions are missing
        editActions = ('cut', 'copy', 'paste', 'delete')
        for a in editActions:
            self.removeActionFromTool(a)
        reorderObjectButtons(self.portal, [])

    def testAllowMembersToViewGroups(self):
        # Should add Member to the list of roles for 'View Groups' permission
        self.portal.manage_permission('View Groups',('Manager',),0)
        member_has_permission = [p for p in
                                    self.portal.permissionsOfRole('Member')
                                            if p['name'] == 'View Groups'][0]
        self.failIf(member_has_permission['selected'])
        allowMembersToViewGroups(self.portal, [])
        member_has_permission = [p for p in
                                    self.portal.permissionsOfRole('Member')
                                            if p['name'] == 'View Groups'][0]
        self.failUnless(member_has_permission['selected'])

    def testReorderStylesheets_rc3_final(self):
        cssreg = self.portal.portal_css

        desired_order = [
            'base.css',
            'public.css',
            'columns.css',
            'authoring.css',
            'portlets.css',
            'presentation.css',
            'print.css',
            'mobile.css',
            'deprecated.css',
            'generated.css',
            'member.css',
            'RTL.css',
            'textSmall.css',
            'textLarge.css',
            # ploneCustom.css is at the bottom by default
        ]

        stylesheet_ids = cssreg.getResourceIds()
        for index, value in enumerate(desired_order):
            self.assertEqual(value, stylesheet_ids[index])

        # do migration again
        reorderStylesheets_rc3_final(self.portal, [])

        stylesheet_ids = cssreg.getResourceIds()
        for index, value in enumerate(desired_order):
            self.assertEqual(value, stylesheet_ids[index])

    def testReplaceMailHost(self):
        # Make sure it converts the  mail host and its settings
        self.portal._delObject('MailHost')
        self.portal._setObject('MailHost', BogusMailHost())
        mailer = self.portal.MailHost
        self.assertEqual(mailer.meta_type, 'Bad Mailer')
        replaceMailHost(self.portal, [])
        mailer = getattr(self.portal, 'MailHost', None)
        self.failUnless(mailer is not None)
        self.assertEqual(mailer.meta_type, 'Secure Mail Host')
        self.assertEqual(mailer.title, 'Mailer')
        self.assertEqual(mailer.smtp_port, 37)
        self.assertEqual(mailer.smtp_host, 'my.badhost.com')

    def testReplaceMailHostWhenMissing(self):
        # Make sure it adds a new one if the original is missing
        self.portal._delObject('MailHost')
        replaceMailHost(self.portal, [])
        mailer = getattr(self.portal, 'MailHost', None)
        self.failUnless(mailer is not None)
        self.assertEqual(mailer.meta_type, 'Secure Mail Host')


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
#        self.cc = self.portal.cookie_authentication
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

    def testRemoveCMFTopicSkinPathFromTableless(self):
        # Should remove plone_3rdParty/CMFTopic from skin paths
        self.addSkinLayer('plone_3rdParty/CMFTopic', skin='Plone Tableless')
        removeCMFTopicSkinLayer(self.portal, [])
        path = self.skins.getSkinPath('Plone Tableless')
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
        editActions = ('cut', 'copy', 'paste', 'delete', 'rename')
        self.removeActionFromTool('rename', 'object_buttons')
        addRenameObjectButton(self.portal, [])
        actions = [x.id for x in self.actions.listActions()
                   if x.category == 'object_buttons']
        self.assertEqual(actions, list(editActions))

    def testAddRenameObjectButtonTwice(self):
        # Should not fail if migrated again
        editActions = ('cut', 'copy', 'paste', 'delete', 'rename')
        self.removeActionFromTool('rename', 'object_buttons')
        addRenameObjectButton(self.portal, [])
        addRenameObjectButton(self.portal, [])
        actions = [x.id for x in self.actions.listActions()
                   if x.category == 'object_buttons']
        self.assertEqual(actions, list(editActions))

    def testAddRenameObjectButtonActionExists(self):
        # Should add 'rename' object_button action
        editActions = ('cut', 'copy', 'paste', 'delete', 'rename')
        addRenameObjectButton(self.portal, [])
        actions = [x.id for x in self.actions.listActions()
                   if x.category == 'object_buttons']
        self.assertEqual(actions, list(editActions))

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
        skins = ['Plone Default', 'Plone Tableless']
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
        self.assertEqual(self.skins.getSkinPath('Plone Tableless').split(',')[-3],
                         'plone_deprecated')

    def testInstallDeprecatedTwice(self):
        # Remove skin
        self.skins._delObject('plone_deprecated')
        skins = ['Plone Default', 'Plone Tableless']
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
        self.assertEqual(self.skins.getSkinPath('Plone Tableless').split(',')[-3],
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
            posHST = jsreg.getResourcePosition('dropdown.js')
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
        paste = tool.getActionObject('object_buttons/paste')
        rename = tool.getActionObject('object_buttons/rename')
        contents = tool.getActionObject('object/folderContents')
        index = tool.getActionObject('portal_tabs/index_html')
        # Should work across multiple tools
        wkspace = self.portal.portal_membership.getActionObject(
                                                           'user/myworkspace')
        # Set the expressions and conditions to their 2.5 analogues to test
        # every substitution
        paste.setActionExpression(
'python:"%s/object_paste"%((object.isDefaultPageInFolder() or not object.is_folderish()) and object.getParentNode().absolute_url() or object_url)')
        rename.setActionExpression(
'python:"%s/object_rename"%(object.isDefaultPageInFolder() and object.getParentNode().absolute_url() or object_url)')
        rename.edit(condition=
'python:portal.portal_membership.checkPermission("Delete objects", object.aq_inner.getParentNode()) and portal.portal_membership.checkPermission("Copy or Move", object) and portal.portal_membership.checkPermission("Add portal content", object) and object is not portal and not (object.isDefaultPageInFolder() and object.getParentNode() is portal)')
        contents.setActionExpression(
"python:((object.isDefaultPageInFolder() and object.getParentNode().absolute_url()) or folder_url)+'/folder_contents'")
        index.setActionExpression(
"string: ${here/@@plone/navigationRootUrl}")
        wkspace.setActionExpression(
"python: portal.portal_membership.getHomeUrl()+'/workspace'")

        # Verify that the changes have been made
        paste = tool.getActionObject('object_buttons/paste')
        self.failUnless("object.isDefaultPageInFolder()" in
                                                  paste.getActionExpression())
        # Run the action simplifications
        simplifyActions(self.portal, [])
        self.assertEqual(paste.getActionExpression(),
                "string:${globals_view/getCurrentFolderUrl}/object_paste")
        self.assertEqual(rename.getActionExpression(),
                "string:${globals_view/getCurrentObjectUrl}/object_rename")
        self.assertEqual(rename.getCondition(),
'python:checkPermission("Delete objects", globals_view.getParentObject()) and checkPermission("Copy or Move", object) and checkPermission("Add portal content", object) and not globals_view.isPortalOrPortalDefaultPage()')
        self.assertEqual(contents.getActionExpression(),
                "string:${globals_view/getCurrentFolderUrl}/folder_contents")
        self.assertEqual(index.getActionExpression(),
                "string:${globals_view/navigationRootUrl}")
        self.assertEqual(wkspace.getActionExpression(),
                "string:${portal/portal_membership/getHomeUrl}/workspace")

    def testSimplifyActionsTwice(self):
        # Should result in the same string when applied twice
        tool = self.portal.portal_actions
        paste = tool.getActionObject('object_buttons/paste')
        paste.setActionExpression(
'python:"%s/object_paste"%((object.isDefaultPageInFolder() or not object.is_folderish()) and object.getParentNode().absolute_url() or object_url)')

        # Verify that the changes have been made
        paste = tool.getActionObject('object_buttons/paste')
        self.failUnless("object.isDefaultPageInFolder()" in
                                                  paste.getActionExpression())

        # Run the action simplifications twice
        simplifyActions(self.portal, [])
        simplifyActions(self.portal, [])

        # We should have the same result
        self.assertEqual(paste.getActionExpression(),
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

    def testFixObjDeleteActionNoAction(self):
        # sould fix the action expression for the action
        editActions = ('delete',)
        newactions = self.actions._cloneActions()
        for a in newactions:
            if a['id'] in editActions:
                a.action = ''
        self.actions._actions = actions
        fixObjDeleteAction(self.portal, [])
        found = 0
        # test that our actions have been altered
        for a in self.actions._cloneActions():
            if a['id'] in editActions:
                self.failUnless(a.action)
                found = found + 1
        # Check that we found the right number of actions
        self.assertEqual(found, len(editActions))

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
        actions = [x.id for x in self.actions.listActions()
                   if x.id in editActions]
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
        self.failIf(Set(self.mimetypes.list_mimetypes()).issuperset(Set(missing_types)))
        out = []
        addMissingMimeTypes(self.portal, out)
        # now they're back:
        self.failUnless(Set(self.mimetypes.list_mimetypes()).issuperset(Set(missing_types)))

class TestMigrations_v2_5_4(MigrationTest):

    def afterSetUp(self):
        self.setup = self.portal.portal_setup

    def testAddGSSteps(self):
        # unset the gs profile
        self.setup._import_context_id = ''
        self.assertEqual(self.setup.getImportContextID(), '')
        addGSSteps(self.portal, [])
        self.assertEqual(self.setup.getImportContextID(),
                         PROF_ID)

    def testAddGSStepsAlreadyThere(self):
        # set a bogus existing profile, ensure we don't change it
        self.setup._import_context_id = 'profile-Bogus:bogus'
        self.assertEqual(self.setup.getImportContextID(),
                         'profile-Bogus:bogus')
        addGSSteps(self.portal, [])
        self.assertEqual(self.setup.getImportContextID(),
                         'profile-Bogus:bogus')

    def testAddGSStepsNoPloneStep(self):
        # if the plone step is not there, don't set it
        # first remove it from the registry
        self.setup._import_context_id = ''
        from Products.GenericSetup.registry import _profile_registry
        _profile_registry._profile_ids.remove(PROF_ID)
        prof_info = _profile_registry._profile_info[PROF_ID]
        del _profile_registry._profile_info[PROF_ID]

        # Then go through the normal migration process
        self.assertEqual(self.setup.getImportContextID(),
                         '')
        addGSSteps(self.portal, [])
        self.assertEqual(self.setup.getImportContextID(),
                         '')
        # restore registry, because this is not undone by the transaction
        _profile_registry._profile_ids.append(PROF_ID)
        _profile_registry._profile_info[PROF_ID] = prof_info

    def testAddGSStepsNoTool(self):
        # do nothing if there's no tool
        self.portal._delObject('portal_setup')
        addGSSteps(self.portal, [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v2))
    suite.addTest(makeSuite(TestMigrations_v2_1))
    suite.addTest(makeSuite(TestMigrations_v2_1_1))
    suite.addTest(makeSuite(TestMigrations_v2_1_2))
    suite.addTest(makeSuite(TestMigrations_v2_1_3))
    suite.addTest(makeSuite(TestMigrations_v2_5))
    suite.addTest(makeSuite(TestMigrations_v2_5_1))
    suite.addTest(makeSuite(TestMigrations_v2_5_2))
    suite.addTest(makeSuite(TestMigrations_v2_5_4))

    return suite

if __name__ == '__main__':
    framework()
