#
# Tests for migration components
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

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
from Products.CMFPlone.migrations.v2_1.alphas import addExclude_from_navMetadata
from Products.CMFPlone.migrations.v2_1.alphas import addIs_FolderishMetadata
from Products.CMFPlone.migrations.v2_1.alphas import indexMembersFolder
from Products.CMFPlone.migrations.v2_1.alphas import addEditContentActions
from Products.CMFPlone.migrations.v2_1.alphas import migrateDateIndexes
from Products.CMFPlone.migrations.v2_1.alphas import migrateDateRangeIndexes
from Products.CMFPlone.migrations.v2_1.alphas import addSortable_TitleIndex
from Products.CMFPlone.migrations.v2_1.alphas import addDefaultTypesToPortalFactory
from Products.CMFPlone.migrations.v2_1.alphas import addNewsTopic
from Products.CMFPlone.migrations.v2_1.alphas import addDisableFolderSectionsSiteProperty


class MigrationTest(PloneTestCase.PloneTestCase):

    def removeActionFromType(self, type_name, action_id):
        # Removes an action from a portal type
        tool = getattr(self.portal, 'portal_types')
        info = tool.getTypeInfo(type_name)
        typeob = getattr(tool, info.getId())
        actions = info.listActions()
        actions = [x for x in actions if x.id != action_id]
        typeob._actions = tuple(actions)

    def removeActionFromTool(self, action_id):
        # Removes an action from portal_actions
        tool = getattr(self.portal, 'portal_actions')
        actions = tool.listActions()
        actions = [x for x in actions if x.id != action_id]
        tool._actions = tuple(actions)

    def removeActionIconFromTool(self, action_id):
        # Removes an action icon from portal_actionicons
        tool = getattr(self.portal, 'portal_actionicons')
        try:
            tool.removeActionIcon('plone', action_id)
        except KeyError:
            pass # No icon associated

    def addActionToTool(self, action_id, category):
        # Adds an action to portal_actions
        tool = getattr(self.portal, 'portal_actions')
        tool.addAction(action_id, action_id, '', '', '', category)

    def removeSiteProperty(self, property_id):
        # Removes a site property from portal_properties
        tool = getattr(self.portal, 'portal_properties')
        sheet = getattr(tool, 'site_properties')
        if sheet.hasProperty(property_id):
            sheet.manage_delProperties([property_id])

    def removeNavTreeProperty(self, property_id):
        # Removes a navtree property from portal_properties
        tool = getattr(self.portal, 'portal_properties')
        sheet = getattr(tool, 'navtree_properties')
        if sheet.hasProperty(property_id):
            sheet.manage_delProperties([property_id])

    def uninstallProduct(self, product_name):
        # Removes a product
        tool = getattr(self.portal, 'portal_quickinstaller')
        if tool.isProductInstalled(product_name):
            tool.uninstallProducts([product_name])


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
        self.uninstallProduct('ResourceRegistries')
        self.failIf(hasattr(self.portal, 'portal_css'))
        installCSSandJSRegistries(self.portal, [])
        self.failUnless('portal_css' in self.portal.objectIds())
        self.failUnless('portal_javascripts' in self.portal.objectIds())

    def testInstallCSSandJSRegistriesTwice(self):
        # Should not fail if migrated again
        self.uninstallProduct('ResourceRegistries')
        self.failIf(hasattr(self.portal, 'portal_css'))
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
        self.failIf('Members' in [x.id for x in self.actions.listActions()])
        self.failIf('news' in [x.id for x in self.actions.listActions()])

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
        # Should not fail if portal_actions is missing
        removePortalTabsActions(self.portal, [])
        removePortalTabsActions(self.portal, [])
        self.failIf('Members' in [x.id for x in self.actions.listActions()])
        self.failIf('news' in [x.id for x in self.actions.listActions()])

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
        news = self.portal.news
        news._delObject('news_topic')
        self.failIf('news_topic' in news.objectIds())
        addNewsTopic(self.portal, [])
        self.failUnless('news_topic' in news.objectIds())
        topic = getattr(news.aq_base, 'news_topic')
        self.assertEqual(topic._getPortalTypeName(), 'Topic')

    def testAddNewsTopicTwice(self):
        #Should not fail if done twice
        news = self.portal.news
        news._delObject('news_topic')
        self.failIf('news_topic' in news.objectIds())
        addNewsTopic(self.portal, [])
        addNewsTopic(self.portal, [])
        self.failUnless('news_topic' in news.objectIds())

    def testAddNewsTopicNoATCT(self):
        #Should not do anything unless ATCT is installed
        news = self.portal.news
        news._delObject('news_topic')
        self.portal._delObject('portal_atct')
        addNewsTopic(self.portal, [])
        self.failUnless('news_topic' not in news.objectIds())

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
        self.catalog.delColumn('is_folderish')
        addIs_FolderishMetadata(self.portal, [])
        self.failUnless('is_folderish' in self.catalog.schema())

    def testAddIs_FolderishMetadataTwice(self):
        # Should not fail if migrated again
        self.catalog.delColumn('is_folderish')
        addIs_FolderishMetadata(self.portal, [])
        addIs_FolderishMetadata(self.portal, [])
        self.failUnless('is_folderish' in self.catalog.schema())

    def testAddIs_FolderishMetadataNoCatalog(self):
        # Should not fail if catalog is missing
        self.portal._delObject('portal_catalog')
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

    def testAddEditcontentActionsTwice(self):
        # Should add the edit-content actions
        editActions = ('cut', 'copy', 'paste', 'delete', 'batch')
        for a in editActions:
            self.removeActionFromTool(a)
        addEditContentActions(self.portal, [])
        addEditContentActions(self.portal, [])
        actions = [x.id for x in self.actions.listActions()]
        for a in editActions:
            self.failUnless(a in actions)

    def testAddEditcontentActionsNoTool(self):
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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v2))
    suite.addTest(makeSuite(TestMigrations_v2_1))
    return suite

if __name__ == '__main__':
    framework()
