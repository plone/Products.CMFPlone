#
# Tests for migration components
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

from OFS.SimpleItem import SimpleItem
from Products.CMFCore.Expression import Expression
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFCore.interfaces import IActionCategory
from Products.CMFCore.interfaces import IActionInfo
from Products.CMFPlone.PloneTool import AllowSendto
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.UnicodeSplitter import Splitter, CaseNormalizer

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

from Products.CMFPlone.migrations.v3_0.alphas import enableZope3Site

from zope.app.component.hooks import clearSite
from zope.app.component.interfaces import ISite
from zope.component import getGlobalSiteManager
from zope.component import getSiteManager

from Products.CMFDynamicViewFTI.migrate import migrateFTI
from Products.Five.component import disableSite

import types

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
        actions = self.actions.object_buttons.objectIds()
        self.assertEqual(actions, list(editActions))

    def testAddRenameObjectButtonTwice(self):
        # Should not fail if migrated again
        editActions = ('cut', 'copy', 'paste', 'delete', 'rename')
        self.removeActionFromTool('rename', 'object_buttons')
        addRenameObjectButton(self.portal, [])
        addRenameObjectButton(self.portal, [])
        actions = self.actions.object_buttons.objectIds()
        self.assertEqual(actions, list(editActions))

    def testAddRenameObjectButtonActionExists(self):
        # Should add 'rename' object_button action
        editActions = ('cut', 'copy', 'paste', 'delete', 'rename')
        addRenameObjectButton(self.portal, [])
        actions = self.actions.object_buttons.objectIds()
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
        paste = tool.object_buttons.paste
        rename = tool.object_buttons.rename
        contents = tool.object.folderContents
        index = tool.portal_tabs.index_html
        wkspace = tool.user.myworkspace
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
        wkspace._updateProperty('url_expr',
                                "python: portal.portal_membership.getHomeUrl()+'/workspace'")

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
        self.assertEqual(wkspace.getProperty('url_expr'),
                "string:${portal/portal_membership/getHomeUrl}/workspace")

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


class TestMigrations_v3_0(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.skins = self.portal.portal_skins
        self.types = self.portal.portal_types
        self.workflow = self.portal.portal_workflow

    def testEnableZope3Site(self):
        # First we remove the site and site manager
        disableSite(self.portal)
        clearSite(self.portal)
        self.portal.setSiteManager(None)

        # Then run the migration step
        enableZope3Site(self.portal, [])
        
        # And see if we have an ISite with a local site manager
        self.failUnless(ISite.providedBy(self.portal))
        gsm = getGlobalSiteManager()
        sm = getSiteManager(self.portal)
        self.failIf(gsm is sm)

    def testEnableZope3SiteTwice(self):
        # First we remove the site and site manager
        disableSite(self.portal)
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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v2_1_1))
    suite.addTest(makeSuite(TestMigrations_v2_1_2))
    suite.addTest(makeSuite(TestMigrations_v2_1_3))
    suite.addTest(makeSuite(TestMigrations_v2_5))
    suite.addTest(makeSuite(TestMigrations_v2_5_1))
    suite.addTest(makeSuite(TestMigrations_v3_0))

    return suite

if __name__ == '__main__':
    framework()
