from plone.registry.interfaces import IRegistry
from Products.CMFPlone.browser.navigation import CatalogNavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import CatalogNavigationTabs
from Products.CMFPlone.browser.navigation import CatalogSiteMap
from Products.CMFPlone.browser.navigation import PhysicalNavigationBreadcrumbs
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.interfaces import ITypesSchema
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests.utils import folder_position
from Products.CMFPlone.tests.utils import validateCSSIdentifier
from zope.component import getUtility
from zope.interface import directlyProvides

import random
import string

portal_name = PloneTestCase.portal_name


class TestBaseNavTree(PloneTestCase.PloneTestCase):
    """Tests for the navigation tree . This base test is a little geared toward
       a catalog based implementation for now.
    """

    view_class = None

    def afterSetUp(self):
        self.request = self.app.REQUEST
        self.populateSite()
        self.setupAuthenticator()
        registry = getUtility(IRegistry)
        self.navigation_settings = registry.forInterface(
            INavigationSchema,
            prefix='plone'
        )

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        self.portal.invokeFactory('Link', 'link1')
        self.portal.link1.remoteUrl = 'http://plone.org'
        self.portal.link1.reindexObject()
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
        self.assertTrue(tree)
        self.assertTrue('children' in tree)

    def testCreateNavTreeCurrentItem(self):
        # With the context set to folder2 it should return a dict with
        # currentItem set to True
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(tree['children'][-1]['currentItem'], True)

    def testNavTreeExcludesItemsWithExcludeProperty(self):
        # Make sure that items witht he exclude_from_nav property set get
        # no_display set to True
        self.portal.folder2.exclude_from_nav = True
        self.portal.folder2.reindexObject()
        view = self.view_class(self.portal.folder1.doc11, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        for c in tree['children']:
            if c['item'].getPath() == '/plone/folder2':
                self.fail()

    def testShowAllParentsOverridesNavTreeExcludesItemsWithExcludeProp(self):
        # Make sure excluded items are not included in the navtree
        self.portal.folder2.exclude_from_nav = True
        self.portal.folder2.reindexObject()
        self.navigation_settings.show_excluded_items = True

        view = self.view_class(self.portal.folder2.doc21, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        found = False
        for c in tree['children']:
            if c['item'].getPath() == '/plone/folder2':
                found = True
                break
        self.assertTrue(found)

    def testNavTreeExcludesDefaultPage(self):
        # Make sure that items which are the default page are excluded
        self.portal.folder2.setDefaultPage('doc21')
        view = self.view_class(self.portal.folder1.doc11, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        # Ensure that our 'doc21' default page is not in the tree.
        self.assertEqual(
            [c for c in tree['children'][-1]['children']
             if c['item'].getPath()[-5:] == 'doc21'],
            []
        )

    def testCreateNavTreeWithLink(self):
        # BBB getRemoteURL deprecated, remove in Plone 4
        view = self.view_class(self.portal, self.request)
        tree = view.navigationTree()
        for child in tree['children']:
            if child['portal_type'] != 'Link':
                self.assertFalse(child['item'].getRemoteUrl)
            if child['Title'] == 'link1':
                self.assertEqual(
                    child['item'].getRemoteUrl,
                    'http://plone.org'
                )

    def testNonStructuralFolderHidesChildren(self):
        # Make sure NonStructuralFolders act as if parent_types_not_to_query
        # is set.
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        self.portal.portal_catalog.reindexObject(self.folder.ns_folder)
        self.portal.portal_catalog.reindexObject(self.folder)
        self.navigation_settings.root = '/Members/test_user_1_'
        view = self.view_class(self.folder.ns_folder, self.request)
        tree = view.navigationTree()
        self.assertEqual(
            tree['children'][0]['item'].getPath(),
            '/plone/Members/test_user_1_/ns_folder'
        )
        self.assertEqual(len(tree['children'][0]['children']), 0)

    def testTopLevel(self):
        ntp = self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(topLevel=1)
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree['children'][-1]['item'].getPath(),
            '/plone/folder2/file21'
        )

    def testTopLevelWithContextAboveLevel(self):
        ntp = self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(topLevel=1)
        view = self.view_class(self.portal, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree['children']), 0)

    def testTopLevelTooDeep(self):
        ntp = self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(topLevel=5)
        view = self.view_class(self.portal, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree['children']), 0)

    def testTopLevelWithNavigationRoot(self):
        self.portal.folder2.invokeFactory('Folder', 'folder21')
        self.portal.folder2.folder21.invokeFactory('Document', 'doc211')
        self.navigation_settings.root = '/folder2'
        ntp = self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(topLevel=1)
        view = self.view_class(self.portal.folder2.folder21, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(len(tree['children']), 1)
        self.assertEqual(tree['children'][0]['item'].getPath(),
                         '/plone/folder2/folder21/doc211')

    def testTopLevelWithPortalFactory(self):
        cid = ''.join(
            [random.choice(string.ascii_lowercase) for x in range(10)]
        )
        typeName = 'Document'
        newObject = self.portal.folder1.restrictedTraverse(
            'portal_factory/' + typeName + '/' + cid)
        # Will raise a KeyError unless bug is fixed
        view = self.view_class(newObject, self.request)
        view.navigationTree()

    def testShowAllParentsOverridesBottomLevel(self):
        ntp = self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(bottomLevel=1)
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        # Note: showAllParents makes sure we actually return items on the,
        # path to the context, but the portlet will not display anything
        # below bottomLevel.
        self.assertEqual(tree['children'][-1]['item'].getPath(),
                         '/plone/folder2')
        self.assertEqual(len(tree['children'][-1]['children']), 1)
        self.assertEqual(tree['children'][-1]['children'][0]['item'].getPath(),
                         '/plone/folder2/file21')

    def testBottomLevelStopsAtFolder(self):
        ntp = self.portal.portal_properties.navtree_properties
        ntp.manage_changeProperties(bottomLevel=1)
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(tree['children'][-1]['item'].getPath(),
                         '/plone/folder2')
        self.assertEqual(len(tree['children'][-1]['children']), 0)

    def testNoRootSet(self):
        self.navigation_settings.root = ''
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(tree['children'][-1]['item'].getPath(),
                         '/plone/folder2')

    def testRootIsPortal(self):
        self.navigation_settings.root = '/'
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(tree['children'][-1]['item'].getPath(),
                         '/plone/folder2')

    def testRootIsNotPortal(self):
        self.navigation_settings.root = '/folder2'
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(tree['children'][0]['item'].getPath(),
                         '/plone/folder2/doc21')

    def testRootDoesNotExist(self):
        self.navigation_settings.root = '/dodo'
        view = self.view_class(self.portal.folder2.file21, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(tree.get('item', None), None)
        self.assertEqual(len(tree['children']), 0)

    def testAboveRoot(self):
        self.navigation_settings.root = '/folder2'
        view = self.view_class(self.portal, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree['children'][0]['item'].getPath(),
            '/plone/folder2/doc21'
        )

    def testOutsideRoot(self):
        self.navigation_settings.root = '/folder2'
        view = self.view_class(self.portal.folder1, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree['children'][0]['item'].getPath(),
            '/plone/folder2/doc21'
        )

    def testRootIsCurrent(self):
        view = self.view_class(self.portal.folder2,
                               self.request,
                               currentFolderOnly=True)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertEqual(
            tree['children'][0]['item'].getPath(),
            '/plone/folder2/doc21'
        )

    def testCustomQuery(self):
        # Try a custom query script for the navtree that returns only published
        # objects
        self.portal._delObject('Members')
        self.portal._delObject('news')
        self.portal._delObject('events')
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getCustomNavQuery')
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit('', 'return {"review_state":"published"}')
        self.assertEqual(self.portal.getCustomNavQuery(),
                         {"review_state": "published"})
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertTrue('children' in tree)
        # Should only contain current object
        self.assertEqual(len(tree['children']), 1)
        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        # Should only contain current object and published folder
        self.assertEqual(len(tree['children']), 2)

    def testStateFiltering(self):
        # Test Navtree workflow state filtering
        self.portal._delObject('Members')
        self.portal._delObject('news')
        self.portal._delObject('events')
        workflow = self.portal.portal_workflow

        self.navigation_settings.workflow_states_to_show = ('published',)
        self.navigation_settings.filter_on_workflow = True
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        self.assertTrue(tree)
        self.assertTrue('children' in tree)
        # Should only contain current object
        self.assertEqual(len(tree['children']), 1)
        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal.folder2, self.request)
        tree = view.navigationTree()
        # Should only contain current object and published folder
        self.assertEqual(len(tree['children']), 2)


class TestSiteMap(PloneTestCase.PloneTestCase):
    """Tests for the sitemap view implementations. This base test is a little
        geared toward a catalog based implementation for now.
    """

    view_class = CatalogSiteMap

    def afterSetUp(self):
        self.request = self.app.REQUEST
        # Apply a default layer for view lookups to work in Zope 2.9+
        self.populateSite()
        registry = getUtility(IRegistry)
        self.navigation_settings = registry.forInterface(
            INavigationSchema,
            prefix='plone'
        )

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        self.portal.invokeFactory('Link', 'link1')
        self.portal.link1.remoteUrl = 'http://plone.org'
        self.portal.link1.reindexObject()
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

    def testCreateSitemap(self):
        view = self.view_class(self.portal, self.request)
        tree = view.siteMap()
        self.assertTrue(tree)

    def testComplexSitemap(self):
        # create and test a reasonabley complex sitemap
        def path(x):
            return '/'.join(x.getPhysicalPath())
        # We do this in a strange order in order to maximally demonstrate the
        # bug
        folder1 = self.portal.folder1
        folder1.invokeFactory('Folder', 'subfolder1')
        subfolder1 = folder1.subfolder1
        folder1.invokeFactory('Folder', 'subfolder2')
        subfolder2 = folder1.subfolder2
        subfolder1.invokeFactory('Folder', 'subfolder11')
        subfolder11 = subfolder1.subfolder11
        subfolder1.invokeFactory('Folder', 'subfolder12')
        subfolder2.invokeFactory('Folder', 'subfolder21')
        subfolder21 = subfolder2.subfolder21
        folder1.invokeFactory('Folder', 'subfolder3')
        subfolder3 = folder1.subfolder3
        subfolder2.invokeFactory('Folder', 'subfolder22')
        subfolder22 = subfolder2.subfolder22
        subfolder22.invokeFactory('Folder', 'subfolder221')
        subfolder221 = subfolder22.subfolder221

        # Increase depth
        self.portal.portal_registry['plone.sitemap_depth'] = 5

        view = self.view_class(self.portal, self.request)
        sitemap = view.siteMap()

        folder1map = sitemap['children'][6]
        self.assertEqual(len(folder1map['children']), 6)
        self.assertEqual(folder1map['item'].getPath(), path(folder1))

        subfolder1map = folder1map['children'][3]
        self.assertEqual(subfolder1map['item'].getPath(), path(subfolder1))
        self.assertEqual(len(subfolder1map['children']), 2)

        subfolder2map = folder1map['children'][4]
        self.assertEqual(subfolder2map['item'].getPath(), path(subfolder2))
        self.assertEqual(len(subfolder2map['children']), 2)

        subfolder3map = folder1map['children'][5]
        self.assertEqual(subfolder3map['item'].getPath(), path(subfolder3))
        self.assertEqual(len(subfolder3map['children']), 0)

        subfolder11map = subfolder1map['children'][0]
        self.assertEqual(subfolder11map['item'].getPath(), path(subfolder11))
        self.assertEqual(len(subfolder11map['children']), 0)

        subfolder21map = subfolder2map['children'][0]
        self.assertEqual(subfolder21map['item'].getPath(), path(subfolder21))
        self.assertEqual(len(subfolder21map['children']), 0)

        subfolder22map = subfolder2map['children'][1]
        self.assertEqual(subfolder22map['item'].getPath(), path(subfolder22))
        self.assertEqual(len(subfolder22map['children']), 1)

        # Why isn't this showing up in the sitemap
        subfolder221map = subfolder22map['children'][0]
        self.assertEqual(subfolder221map['item'].getPath(), path(subfolder221))
        self.assertEqual(len(subfolder221map['children']), 0)

    def testSitemapUnchangedWithTopLevel(self):
        # Test that setting topLevel does not alter the sitemap
        ntp = self.portal.portal_properties.navtree_properties
        for topLevel in range(0, 5):
            ntp.manage_changeProperties(topLevel=topLevel)
            view = self.view_class(self.portal, self.request)
            sitemap = view.siteMap()
            self.assertEqual(sitemap['children'][-1]['item'].getPath(),
                             '/plone/folder2')

    def testSitemapUnchangedWithBottomLevel(self):
        # Test that setting bottomLevel does not alter the sitemap
        ntp = self.portal.portal_properties.navtree_properties
        for bottomLevel in range(0, 5):
            ntp.manage_changeProperties(bottomLevel=bottomLevel)
            view = self.view_class(self.portal, self.request)
            sitemap = view.siteMap()
            self.assertEqual(sitemap['children'][-1]['item'].getPath(),
                             '/plone/folder2')
            self.assertTrue(len(sitemap['children'][-1]['children']) > 0)

    def testSitemapWithNavigationRoot(self):
        self.navigation_settings.root = '/folder2'
        view = self.view_class(self.portal, self.request)
        sitemap = view.siteMap()
        self.assertEqual(sitemap['children'][-1]['item'].getPath(),
                         '/plone/folder2/file21')


class TestBasePortalTabs(PloneTestCase.PloneTestCase):
    """Tests for the portal tabs view implementations
       This base test is a little geared toward a catalog based implementation
       for now.
    """

    view_class = None

    def afterSetUp(self):
        self.request = self.app.REQUEST
        self.populateSite()

    @property
    def navigation_settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(
            INavigationSchema,
            prefix='plone'
        )

    def populateSite(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        self.portal.invokeFactory('Folder', 'folder2')
        self.setRoles(['Member'])

    def testCreateTopLevelTabs(self):
        # See if we can create one at all
        view = self.view_class(self.portal, self.request)

        # Everything shows up by default
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        self.assertEqual(len(tabs), 7)

        # Only the folders show up (Members, news, events, folder1, folder2)
        self.navigation_settings.nonfolderish_tabs = False
        tabs = view.topLevelTabs(actions=[])
        self.assertEqual(len(tabs), 4)

    def testTabsRespectFolderOrder(self):
        # See if reordering causes a change in the tab order
        view = self.view_class(self.portal, self.request)
        tabs1 = view.topLevelTabs(actions=[])
        # Must be manager to change order on portal itself
        self.setRoles(['Manager', 'Member'])
        folder_position(self.portal, 'up', 'folder2')
        view = self.view_class(self.portal, self.request)
        tabs2 = view.topLevelTabs(actions=[])
        # Same number of objects
        self.assertEqual(len(tabs1), len(tabs2))
        # Different order
        self.assertTrue(tabs1 != tabs2)

    def testCustomQuery(self):
        # Try a custom query script for the tabs that returns only published
        # objects
        self.portal._delObject('Members')
        self.portal._delObject('news')
        self.portal._delObject('events')
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript('getCustomNavQuery')
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit('', 'return {"review_state":"published"}')
        self.assertEqual(
            self.portal.getCustomNavQuery(), {"review_state": "published"})
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        # Should contain no folders
        self.assertEqual(len(tabs), 0)
        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        # Should only contain the published folder
        self.assertEqual(len(tabs), 1)

    def testStateFiltering(self):
        # Test tabs workflow state filtering
        self.portal._delObject('Members')
        self.portal._delObject('news')
        self.portal._delObject('events')
        workflow = self.portal.portal_workflow

        self.navigation_settings.workflow_states_to_show = ('published',)
        self.navigation_settings.filter_on_workflow = True
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        # Should contain no folders
        self.assertEqual(len(tabs), 0)
        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, 'publish')
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        # Should only contain the published folder
        self.assertEqual(len(tabs), 1)

    def testTabInfo(self):
        self.portal._delObject('Members')
        self.portal._delObject('news')
        self.portal._delObject('events')

        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])

        self.assertEqual(len(tabs), 5)

        tab = tabs[0]
        self.assertTrue('url' in tab and tab['url'])  # url must not be empty
        self.assertTrue('description' in tab)  # our description is empty
        self.assertTrue('name' in tab and tab['name'])
        self.assertTrue('id' in tab and tab['id'])
        self.assertTrue('review_state' in tab and tab['review_state'])

    def testDisableFolderTabs(self):
        # Setting the site_property disable_folder_sections should remove
        # all folder based tabs
        self.navigation_settings.generate_tabs = False
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertEqual(tabs, [])

    def testTabsExcludeItemsWithExcludeProperty(self):
        self.portal.folder2.exclude_from_nav = True
        self.portal.folder2.reindexObject()

        # if we're not in context of the excluded item it should disappear
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        tab_names = [t['id'] for t in tabs]
        self.assertNotIn('folder2', tab_names)

        # if we're inside, it also should stay hidden
        view = self.view_class(self.portal.folder2, self.request)
        tabs = view.topLevelTabs(actions=[])
        tab_names = [t['id'] for t in tabs]
        self.assertNotIn('folder2', tab_names)

        # Now we flip the setting for plone.show_excluded_items
        self.navigation_settings.show_excluded_items = True
        view = self.view_class(self.portal.folder2, self.request)
        tabs = view.topLevelTabs(actions=[])
        tab_names = [t['id'] for t in tabs]
        self.assertIn('folder2', tab_names)

    def testTabsRespectsTypesWithViewAction(self):
        # With a type in types_use_view_action_in_listings as current action it
        # should return a tab which has '/view' appended to the url
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        # Fail if 'view' is used for folder
        self.assertFalse(tabs[-1]['url'][-5:] == '/view')
        # Add Folder to type settings
        registry = getUtility(IRegistry)
        type_settings = registry.forInterface(
            ITypesSchema,
            prefix="plone",
            check=False
        )
        type_settings.types_use_view_action_in_listings = [
            'Image', 'File', 'Folder'
        ]
        # Verify that we have '/view'
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        self.assertEqual(tabs[-1]['url'][-5:], '/view')

    def testTabsExcludeNonFolderishItems(self):
        self.navigation_settings.nonfolderish_tabs = False
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        orig_len = len(tabs)
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Document', 'foo')
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        self.assertEqual(len(tabs), orig_len)

    def testRootBelowPortalRoot(self):
        self.setRoles(['Manager'])
        self.portal.manage_delObjects(['news', 'events', 'Members'])
        self.setRoles(['Member'])
        self.navigation_settings.nonfolderish_tabs = False
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        self.assertEqual(len(tabs), 2)
        self.assertEqual(tabs[0]['id'], 'folder1')
        self.assertEqual(tabs[1]['id'], 'folder2')

    def testPortalTabsNotIncludeViewNamesInCSSid(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('File', 'file1')
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        for tab in tabs:
            self.assertEqual(validateCSSIdentifier(tab['id']), True)

    def testLinkRemoteUrlsUsedUnlessLinkCreator(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Link', 'link1')
        self.portal.link1.remoteUrl = 'http://plone.org'
        self.portal.link1.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        for tab in tabs:
            # as Creator tab for link1 should have url of the item
            if tab['id'] == 'link1':
                self.assertTrue(tab['url'] == 'http://nohost/plone/link1')

        self.setRoles(['Manager'])
        self.portal.link1.setCreators(['some_other_user'])
        self.portal.link1.reindexObject()
        tabs = view.topLevelTabs(actions=[])
        for tab in tabs:
            # as non-Creator user, tab for link1 should have url of the remote
            # url
            if tab['id'] == 'link1':
                self.assertTrue(tab['url'] == 'http://plone.org')


class TestCatalogPortalTabs(TestBasePortalTabs):
    view_class = CatalogNavigationTabs


class TestBaseBreadCrumbs(PloneTestCase.PloneTestCase):
    """Tests for the portal tabs query
    """

    view_class = None

    def afterSetUp(self):
        self.request = self.app.REQUEST
        self.populateSite()
        registry = getUtility(IRegistry)
        self.navigation_settings = registry.forInterface(
            INavigationSchema,
            prefix='plone'
        )

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
        self.assertTrue(crumbs)
        self.assertEqual(len(crumbs), 2)
        self.assertEqual(crumbs[-1]['absolute_url'], doc.absolute_url())
        self.assertEqual(crumbs[-2]['absolute_url'],
                         doc.aq_parent.absolute_url())

    def testBreadcrumbsRespectTypesWithViewAction(self):
        # With a type in types_use_view_action_in_listings as current action it
        # should return a breadcrumb which has '/view' appended to the url
        view = self.view_class(self.portal.folder1.file11, self.request)
        crumbs = view.breadcrumbs()
        self.assertTrue(crumbs)
        self.assertEqual(crumbs[-1]['absolute_url'][-5:], '/view')

    def testBreadcrumbsStopAtNavigationRoot(self):
        self.navigation_settings.top_level = 1
        self.navigation_settings.root = '/folder1'
        view = self.view_class(self.portal.folder1.doc11, self.request)
        crumbs = view.breadcrumbs()
        self.assertTrue(crumbs)
        self.assertEqual(crumbs[0]['absolute_url'],
                         self.portal.folder1.doc11.absolute_url())


class TestCatalogBreadCrumbs(TestBaseBreadCrumbs):

    view_class = CatalogNavigationBreadcrumbs


class TestPhysicalBreadCrumbs(TestBaseBreadCrumbs):

    view_class = PhysicalNavigationBreadcrumbs

    def testBreadcrumbsFilterByInterface(self):
        view = self.view_class(self.portal.folder1.doc11, self.request)
        crumbs = view.breadcrumbs()
        directlyProvides(self.portal.folder1, IHideFromBreadcrumbs)
        newcrumbs = view.breadcrumbs()
        self.assertEqual(len(crumbs) - 1, len(newcrumbs))
        self.assertEqual(newcrumbs[-1]['absolute_url'],
                         self.portal.folder1.doc11.absolute_url())

    def testBreadcrumbsFilterByInterface2(self):
        # Test url of subfolder of hidden folder.
        self.portal.folder1.invokeFactory('Folder', 'subfolder11')
        directlyProvides(self.portal.folder1.subfolder11, IHideFromBreadcrumbs)
        self.portal.folder1.subfolder11.invokeFactory('Folder', 'subfolder111')
        self.portal.folder1.subfolder11.subfolder111.invokeFactory(
            'Document', 'doc1111')
        doc1111 = self.portal.folder1.subfolder11.subfolder111.doc1111
        view = self.view_class(doc1111, self.request)
        newcrumbs = view.breadcrumbs()
        self.assertEqual(
            newcrumbs[-2]['absolute_url'],
            self.portal.folder1.subfolder11.subfolder111.absolute_url()
            )



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCatalogPortalTabs))
    suite.addTest(makeSuite(TestSiteMap))
    suite.addTest(makeSuite(TestCatalogBreadCrumbs))
    suite.addTest(makeSuite(TestPhysicalBreadCrumbs))
    return suite
