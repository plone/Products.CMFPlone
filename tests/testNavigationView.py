#
# Test methods used to make ...
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))
try:
    from zope.app.publication.browser import setDefaultSkin
    ZOPE28 = False
except ImportError:
    ZOPE28 = True

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import dummy
PloneTestCase.setupPloneSite()

from Products.CMFPlone.utils import _createObjectByType

from Products.CMFPlone.browser.navigation import CatalogNavigationTree
from Products.CMFPlone.browser.navigation import CatalogNavigationTabs
from Products.CMFPlone.browser.navigation import CatalogNavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import PhysicalNavigationBreadcrumbs

portal_name = PloneTestCase.portal_name


class TestBaseNavTree(PloneTestCase.PloneTestCase):
    """Tests for the navigation tree and sitemap view implementations
       This base test is a little geared toward a catalog based implementation
       for now.
    """

    view_class = None

    def afterSetUp(self):
        self.request = self.app.REQUEST
        if not ZOPE28:
            # Apply a default layer for view lookups to work in Zope 2.9+
            setDefaultSkin(self.request)
        self.populateSite()

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('Document', 'doc12')
        folder1.invokeFactory('Document', 'doc13')
        self.portal.invokeFactory('Folder', 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        folder2.invokeFactory('Document', 'doc21')
        folder2.invokeFactory('Document', 'doc22')
        folder2.invokeFactory('Document', 'doc23')
        folder2.invokeFactory('File', 'file21')
        self.setRoles(['Member'])

    def testCreateNavTree(self):
        # See if we can create one at all
        view = self.view_class(self.portal, self.request)
        tree = view.navigationTree()
        self.failUnless(tree)
        self.failUnless(tree.has_key('children'))

    def testCreateNavTreeCurrentItem(self):
        # With the context set to folder2 it should return a dict with
        # currentItem set to True
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['currentItem'], True)

    def testCreateNavTreeRespectsTypesWithViewAction(self):
        # With a File or Image as current action it should return a
        # currentItem which has '/view' appended to the url
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.failUnless(tree)
        # Fail if 'view' is used for parent folder; it should only be on the File
        self.failIf(tree['children'][-1]['absolute_url'][-5:]=='/view')
        # Verify we have the correct object and it is the current item
        entry = tree['children'][-1]['children'][-1]
        self.assertEqual(entry['currentItem'], True)
        self.assertEqual(entry['path'].split('/')[-1],'file21')
        # Verify that we have '/view'
        self.assertEqual(entry['absolute_url'][-5:],'/view')

    def testNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items witht he exclude_from_nav property set get
        # no_display set to True
        self.portal.folder2.setExcludeFromNav(True)
        self.portal.folder2.reindexObject()
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['no_display'],True)
        # Shouldn't exlude anything else
        self.assertEqual(tree['children'][0]['no_display'],False)

    def testNavTreeExcludesItemsInIdsNotToList(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property get no_display set to True
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(idsNotToList=['folder2'])
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.failUnless(tree)
        self.assertEqual(tree['children'][-1]['no_display'],True)
        # Shouldn't exlude anything else
        self.assertEqual(tree['children'][0]['no_display'],False)

    def testNavTreeExcludesDefaultPage(self):
        # Make sure that items which are the default page are excluded
        self.portal.folder2.setDefaultPage('doc21')
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.failUnless(tree)
        # Ensure that our 'doc21' default page is not in the tree.
        self.assertEqual([c for c in tree['children'][-1]['children']
                          if c['path'][-5:]=='doc21'], [])

    def testNavTreeMarksParentMetaTypesNotToQuery(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property get no_display set to True
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.assertEqual(tree['children'][-1]['show_children'],True)
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(parentMetaTypesNotToQuery=['Folder'])
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.assertEqual(tree['children'][-1]['show_children'],False)

    def testNonStructuralFolderHidesChildren(self):
        # Make sure NonStructuralFolders act as if parentMetaTypesNotToQuery
        # is set.
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        self.portal.portal_catalog.reindexObject(self.folder.ns_folder)
        self.portal.portal_catalog.reindexObject(self.folder)
        view = self.view_class(self.folder.ns_folder, self.request)
        tree = view.navigationTree()
        self.assertEqual(
            tree['children'][0]['children'][0]['children'][0]['path'],
            '/%s/Members/test_user_1_/ns_folder' % portal_name)
        self.assertEqual(
            tree['children'][0]['children'][0]['children'][0]['show_children'],
            False)

    def testCreateSitemap(self):
        # Internally createSitemap is the same as createNavTree
        view = self.view_class(self.portal, self.request)
        tree = view.navigationTree(sitemap=True)
        self.failUnless(tree)

    def testCustomQuery(self):
        # Try a custom query script for the navtree that returns only published
        # objects
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getCustomNavQuery')
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit('', 'return {"review_state":"published"}')
        self.assertEqual(
            self.portal.getCustomNavQuery(), {"review_state":"published"})
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        self.failUnless(tree)
        self.failUnless(tree.has_key('children'))
        #Should only contain current object
        self.assertEqual(len(tree['children']), 1)
        #change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        #Should only contain current object and published folder
        self.assertEqual(len(tree['children']), 2)

    def testStateFiltering(self):
        # Test Navtree workflow state filtering
        workflow = self.portal.portal_workflow
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(wf_states_to_show=['published'])
        ntp.manage_changeProperties(enable_wf_state_filtering=True)
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        self.failUnless(tree)
        self.failUnless(tree.has_key('children'))
        #Should only contain current object
        self.assertEqual(len(tree['children']), 1)
        #change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        #Should only contain current object and published folder
        self.assertEqual(len(tree['children']), 2)

    def testComplexSitemap(self):
        # create and test a reasonabley complex sitemap
        path = lambda x: '/'.join(x.getPhysicalPath())
        # We do this in a strange order in order to maximally demonstrate the bug
        folder1 = self.portal.folder1
        folder1.invokeFactory('Folder','subfolder1')
        subfolder1 = folder1.subfolder1
        folder1.invokeFactory('Folder','subfolder2')
        subfolder2 = folder1.subfolder2
        subfolder1.invokeFactory('Folder','subfolder11')
        subfolder11 = subfolder1.subfolder11
        subfolder1.invokeFactory('Folder','subfolder12')
        subfolder12 = subfolder1.subfolder12
        subfolder2.invokeFactory('Folder','subfolder21')
        subfolder21 = subfolder2.subfolder21
        folder1.invokeFactory('Folder','subfolder3')
        subfolder3 = folder1.subfolder3
        subfolder2.invokeFactory('Folder','subfolder22')
        subfolder22 = subfolder2.subfolder22
        subfolder22.invokeFactory('Folder','subfolder221')
        subfolder221 = subfolder22.subfolder221

        # Increase depth
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(sitemapDepth=5)
        view = self.view_class(self.portal, self.request)
        sitemap = view.navigationTree(sitemap=True)

        folder1map = sitemap['children'][6]
        self.assertEqual(len(folder1map['children']), 6)
        self.assertEqual(folder1map['path'], path(folder1))

        subfolder1map = folder1map['children'][3]
        self.assertEqual(subfolder1map['path'], path(subfolder1))
        self.assertEqual(len(subfolder1map['children']), 2)

        subfolder2map = folder1map['children'][4]
        self.assertEqual(subfolder2map['path'], path(subfolder2))
        self.assertEqual(len(subfolder2map['children']), 2)

        subfolder3map = folder1map['children'][5]
        self.assertEqual(subfolder3map['path'], path(subfolder3))
        self.assertEqual(len(subfolder3map['children']), 0)

        subfolder11map = subfolder1map['children'][0]
        self.assertEqual(subfolder11map['path'], path(subfolder11))
        self.assertEqual(len(subfolder11map['children']), 0)

        subfolder21map = subfolder2map['children'][0]
        self.assertEqual(subfolder21map['path'], path(subfolder21))
        self.assertEqual(len(subfolder21map['children']), 0)

        subfolder22map = subfolder2map['children'][1]
        self.assertEqual(subfolder22map['path'], path(subfolder22))
        self.assertEqual(len(subfolder22map['children']), 1)

        # Why isn't this showing up in the sitemap
        subfolder221map = subfolder22map['children'][0]
        self.assertEqual(subfolder221map['path'], path(subfolder221))
        self.assertEqual(len(subfolder221map['children']), 0)

class TestCatalogNavTree(TestBaseNavTree):
        view_class = CatalogNavigationTree


class TestBasePortalTabs(PloneTestCase.PloneTestCase):
    """Tests for the portal tabs view implementations
       This base test is a little geared toward a catalog based implementation
       for now.
    """

    view_class = None

    def afterSetUp(self):
        self.request = self.app.REQUEST
        if not ZOPE28:
            setDefaultSkin(self.request)
        self.populateSite()

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = getattr(self.portal, 'folder1')
        self.portal.invokeFactory('Folder', 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        self.setRoles(['Member'])

    def testCreateTopLevelTabs(self):
        # See if we can create one at all
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        self.failUnless(tabs)
        #Only the folders show up (Members, news, events, folder1, folder2)
        self.assertEqual(len(tabs), 5)

    def testTabsRespectFolderOrder(self):
        # See if reordering causes a change in the tab order
        view = self.view_class(self.portal, self.request)
        tabs1 = view.topLevelTabs()
        # Must be manager to change order on portal itself
        self.setRoles(['Manager','Member'])
        self.portal.folder_position('up', 'folder2')
        view = self.view_class(self.portal, self.request)
        tabs2 = view.topLevelTabs()
        #Same number of objects
        self.failUnlessEqual(len(tabs1), len(tabs2))
        #Different order
        self.failUnless(tabs1 != tabs2)

    def testCustomQuery(self):
        # Try a custom query script for the tabs that returns only published
        # objects
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getCustomNavQuery')
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit('', 'return {"review_state":"published"}')
        self.assertEqual(
            self.portal.getCustomNavQuery(), {"review_state":"published"})
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        #Should contain no folders
        self.assertEqual(len(tabs), 0)
        #change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        #Should only contain the published folder
        self.assertEqual(len(tabs), 1)

    def testStateFiltering(self):
        # Test tabs workflow state filtering
        workflow = self.portal.portal_workflow
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(wf_states_to_show=['published'])
        ntp.manage_changeProperties(enable_wf_state_filtering=True)
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        #Should contain no folders
        self.assertEqual(len(tabs), 0)
        #change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        #Should only contain the published folder
        self.assertEqual(len(tabs), 1)

    def testDisableFolderTabs(self):
        # Setting the site_property disable_folder_sections should remove
        # all folder based tabs
        props = self.portal.portal_properties.site_properties
        props.manage_changeProperties(disable_folder_sections=True)
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        self.assertEqual(tabs, [])

    def testTabsExcludeItemsWithExcludeProperty(self):
        # Make sure that items witht he exclude_from_nav property are purged
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        orig_len = len(tabs)
        self.portal.folder2.setExcludeFromNav(True)
        self.portal.folder2.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        self.failUnless(tabs)
        self.assertEqual(len(tabs), orig_len - 1)
        tab_names = [t['id'] for t in tabs]
        self.failIf('folder2' in tab_names)

    def testTabsRespectsTypesWithViewAction(self):
        # With a type in typesUseViewActionInListings as current action it
        # should return a tab which has '/view' appended to the url
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        self.failUnless(tabs)
        # Fail if 'view' is used for folder
        self.failIf(tabs[-1]['url'][-5:]=='/view')
        # Add Folder to site_property
        props = self.portal.portal_properties.site_properties
        props.manage_changeProperties(
            typesUseViewActionInListings=['Image','File','Folder'])
        # Verify that we have '/view'
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        self.failUnless(tabs)
        self.assertEqual(tabs[-1]['url'][-5:],'/view')

    def testTabsExcludeItemsInIdsNotToList(self):
        # Make sure that items whose ids are in the idsNotToList navTree
        # property get purged
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        orig_len = len(tabs)
        ntp=self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(idsNotToList=['folder2'])
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        self.failUnless(tabs)
        self.assertEqual(len(tabs), orig_len - 1)
        tab_names = [t['id'] for t in tabs]
        self.failIf('folder2' in tab_names)

    def testTabsExcludeNonFolderishItems(self):
        # Make sure that items witht he exclude_from_nav property are purged
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        orig_len = len(tabs)
        self.setRoles(['Manager','Member'])
        self.portal.invokeFactory('Document','foo')
        self.portal.foo.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs()
        self.failUnless(tabs)
        self.assertEqual(len(tabs),orig_len)


class TestCatalogPortalTabs(TestBasePortalTabs):
        view_class = CatalogNavigationTabs


class TestBaseBreadCrumbs(PloneTestCase.PloneTestCase):
    """Tests for the portal tabs query
    """

    view_class = None

    def afterSetUp(self):
        self.request = self.app.REQUEST
        if not ZOPE28:
            setDefaultSkin(self.request)
        self.populateSite()

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'folder1')
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('File', 'file11')
        self.setRoles(['Member'])

    def testCreateBreadCrumbs(self):
        # See if we can create one at all
        doc = self.portal.folder1.doc11
        view = self.view_class(doc, self.request)
        crumbs = view.breadcrumbs()
        self.failUnless(crumbs)
        self.assertEqual(len(crumbs), 2)
        self.assertEqual(crumbs[-1]['absolute_url'], doc.absolute_url())
        self.assertEqual(crumbs[-2]['absolute_url'], doc.aq_parent.absolute_url())

    def testBreadcrumbsRespectTypesWithViewAction(self):
        # With a type in typesUseViewActionInListings as current action it
        # should return a breadcrumb which has '/view' appended to the url
        file = self.portal.folder1.file11
        view = self.view_class(self.portal.folder1.file11, self.request)
        crumbs = view.breadcrumbs()
        self.failUnless(crumbs)
        self.assertEqual(crumbs[-1]['absolute_url'][-5:],'/view')


class TestCatalogBreadCrumbs(TestBaseBreadCrumbs):
        view_class = CatalogNavigationBreadcrumbs


class TestPhysicalBreadCrumbs(TestBaseBreadCrumbs):
        # This effectively tests the RootPhysicalNavigationStructure as well
        view_class = PhysicalNavigationBreadcrumbs


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCatalogPortalTabs))
    suite.addTest(makeSuite(TestCatalogNavTree))
    suite.addTest(makeSuite(TestCatalogBreadCrumbs))
    suite.addTest(makeSuite(TestPhysicalBreadCrumbs))
    return suite

if __name__ == '__main__':
    framework()
