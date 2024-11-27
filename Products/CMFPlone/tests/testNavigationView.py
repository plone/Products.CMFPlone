from plone.base.interfaces import IHideFromBreadcrumbs
from plone.base.interfaces import INavigationSchema
from plone.base.interfaces import ITypesSchema
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.browser.navigation import CatalogNavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import CatalogNavigationTabs
from Products.CMFPlone.browser.navigation import CatalogSiteMap
from Products.CMFPlone.browser.navigation import PhysicalNavigationBreadcrumbs
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests.utils import folder_position
from Products.CMFPlone.tests.utils import validateCSSIdentifier
from zope.component import getUtility
from zope.interface import directlyProvides


portal_name = PloneTestCase.portal_name


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
            INavigationSchema, prefix="plone"
        )

    def populateSite(self):
        self.setRoles(["Manager"])
        self.portal.invokeFactory("Document", "doc1")
        self.portal.invokeFactory("Document", "doc2")
        self.portal.invokeFactory("Document", "doc3")
        self.portal.invokeFactory("Folder", "folder1")
        self.portal.invokeFactory("Link", "link1")
        self.portal.link1.remoteUrl = "http://plone.org"
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, "folder1")
        folder1.invokeFactory("Document", "doc11")
        folder1.invokeFactory("Document", "doc12")
        folder1.invokeFactory("Document", "doc13")
        self.portal.invokeFactory("Folder", "folder2")
        folder2 = getattr(self.portal, "folder2")
        folder2.invokeFactory("Document", "doc21")
        folder2.invokeFactory("Document", "doc22")
        folder2.invokeFactory("Document", "doc23")
        folder2.invokeFactory("File", "file21")
        self.setRoles(["Member"])

    def testCreateSitemap(self):
        view = self.view_class(self.portal, self.request)
        tree = view.siteMap()
        self.assertTrue(tree)

    def testComplexSitemap(self):
        # create and test a reasonabley complex sitemap
        def path(x):
            return "/".join(x.getPhysicalPath())

        # We do this in a strange order in order to maximally demonstrate the
        # bug
        folder1 = self.portal.folder1
        folder1.invokeFactory("Folder", "subfolder1")
        subfolder1 = folder1.subfolder1
        folder1.invokeFactory("Folder", "subfolder2")
        subfolder2 = folder1.subfolder2
        subfolder1.invokeFactory("Folder", "subfolder11")
        subfolder11 = subfolder1.subfolder11
        subfolder1.invokeFactory("Folder", "subfolder12")
        subfolder2.invokeFactory("Folder", "subfolder21")
        subfolder21 = subfolder2.subfolder21
        folder1.invokeFactory("Folder", "subfolder3")
        subfolder3 = folder1.subfolder3
        subfolder2.invokeFactory("Folder", "subfolder22")
        subfolder22 = subfolder2.subfolder22
        subfolder22.invokeFactory("Folder", "subfolder221")
        subfolder221 = subfolder22.subfolder221

        # Increase depth
        self.portal.portal_registry["plone.sitemap_depth"] = 5

        view = self.view_class(self.portal, self.request)
        sitemap = view.siteMap()

        folder1map = sitemap["children"][6]
        self.assertEqual(len(folder1map["children"]), 6)
        self.assertEqual(folder1map["item"].getPath(), path(folder1))

        subfolder1map = folder1map["children"][3]
        self.assertEqual(subfolder1map["item"].getPath(), path(subfolder1))
        self.assertEqual(len(subfolder1map["children"]), 2)

        subfolder2map = folder1map["children"][4]
        self.assertEqual(subfolder2map["item"].getPath(), path(subfolder2))
        self.assertEqual(len(subfolder2map["children"]), 2)

        subfolder3map = folder1map["children"][5]
        self.assertEqual(subfolder3map["item"].getPath(), path(subfolder3))
        self.assertEqual(len(subfolder3map["children"]), 0)

        subfolder11map = subfolder1map["children"][0]
        self.assertEqual(subfolder11map["item"].getPath(), path(subfolder11))
        self.assertEqual(len(subfolder11map["children"]), 0)

        subfolder21map = subfolder2map["children"][0]
        self.assertEqual(subfolder21map["item"].getPath(), path(subfolder21))
        self.assertEqual(len(subfolder21map["children"]), 0)

        subfolder22map = subfolder2map["children"][1]
        self.assertEqual(subfolder22map["item"].getPath(), path(subfolder22))
        self.assertEqual(len(subfolder22map["children"]), 1)

        # Why isn't this showing up in the sitemap
        subfolder221map = subfolder22map["children"][0]
        self.assertEqual(subfolder221map["item"].getPath(), path(subfolder221))
        self.assertEqual(len(subfolder221map["children"]), 0)

    def testSitemapUnchangedWithTopLevel(self):
        # Test that setting topLevel does not alter the sitemap
        ntp = self.portal.portal_properties.navtree_properties
        for topLevel in range(0, 5):
            ntp.manage_changeProperties(topLevel=topLevel)
            view = self.view_class(self.portal, self.request)
            sitemap = view.siteMap()
            self.assertEqual(
                sitemap["children"][-1]["item"].getPath(), "/plone/folder2"
            )

    def testSitemapUnchangedWithBottomLevel(self):
        # Test that setting bottomLevel does not alter the sitemap
        ntp = self.portal.portal_properties.navtree_properties
        for bottomLevel in range(0, 5):
            ntp.manage_changeProperties(bottomLevel=bottomLevel)
            view = self.view_class(self.portal, self.request)
            sitemap = view.siteMap()
            self.assertEqual(
                sitemap["children"][-1]["item"].getPath(), "/plone/folder2"
            )
            self.assertTrue(len(sitemap["children"][-1]["children"]) > 0)

    def testSitemapWithNavigationRoot(self):
        self.navigation_settings.root = "/folder2"
        view = self.view_class(self.portal, self.request)
        sitemap = view.siteMap()
        self.assertEqual(
            sitemap["children"][-1]["item"].getPath(), "/plone/folder2/doc23"
        )


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
        return registry.forInterface(INavigationSchema, prefix="plone")

    def populateSite(self):
        self.setRoles(["Manager"])
        self.portal.invokeFactory("Document", "doc1")
        self.portal.invokeFactory("Document", "doc2")
        self.portal.invokeFactory("Document", "doc3")
        self.portal.invokeFactory("Folder", "folder1")
        self.portal.invokeFactory("Folder", "folder2")
        self.setRoles(["Member"])

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
        self.setRoles(["Manager", "Member"])
        folder_position(self.portal, "up", "folder2")
        view = self.view_class(self.portal, self.request)
        tabs2 = view.topLevelTabs(actions=[])
        # Same number of objects
        self.assertEqual(len(tabs1), len(tabs2))
        # Different order
        self.assertTrue(tabs1 != tabs2)

    def testCustomQuery(self):
        # Try a custom query script for the tabs that returns only published
        # objects
        self.portal._delObject("Members")
        self.portal._delObject("news")
        self.portal._delObject("events")
        workflow = self.portal.portal_workflow
        factory = self.portal.manage_addProduct["PythonScripts"]
        factory.manage_addPythonScript("getCustomNavQuery")
        script = self.portal.getCustomNavQuery
        script.ZPythonScript_edit("", 'return {"review_state":"published"}')
        self.assertEqual(self.portal.getCustomNavQuery(), {"review_state": "published"})
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        # Should contain no folders
        self.assertEqual(len(tabs), 0)
        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, "publish")
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        # Should only contain the published folder
        self.assertEqual(len(tabs), 1)

    def testStateFiltering(self):
        # Test tabs workflow state filtering
        self.portal._delObject("Members")
        self.portal._delObject("news")
        self.portal._delObject("events")
        workflow = self.portal.portal_workflow

        self.navigation_settings.workflow_states_to_show = ("published",)
        self.navigation_settings.filter_on_workflow = True
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        # Should contain no folders
        self.assertEqual(len(tabs), 0)
        # change workflow for folder1
        workflow.doActionFor(self.portal.folder1, "publish")
        self.portal.folder1.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        # Should only contain the published folder
        self.assertEqual(len(tabs), 1)

    def testTabInfo(self):
        self.portal._delObject("Members")
        self.portal._delObject("news")
        self.portal._delObject("events")

        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])

        self.assertEqual(len(tabs), 5)

        tab = tabs[0]
        self.assertTrue("url" in tab and tab["url"])  # url must not be empty
        self.assertTrue("description" in tab)  # our description is empty
        self.assertTrue("name" in tab and tab["name"])
        self.assertTrue("id" in tab and tab["id"])
        self.assertTrue("review_state" in tab and tab["review_state"])

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
        tab_names = [t["id"] for t in tabs]
        self.assertNotIn("folder2", tab_names)

        # if we're inside, it also should stay hidden
        view = self.view_class(self.portal.folder2, self.request)
        tabs = view.topLevelTabs(actions=[])
        tab_names = [t["id"] for t in tabs]
        self.assertNotIn("folder2", tab_names)

        # Now we flip the setting for plone.show_excluded_items
        self.navigation_settings.show_excluded_items = True
        view = self.view_class(self.portal.folder2, self.request)
        tabs = view.topLevelTabs(actions=[])
        tab_names = [t["id"] for t in tabs]
        self.assertIn("folder2", tab_names)

    def testTabsRespectsTypesWithViewAction(self):
        # With a type in types_use_view_action_in_listings as current action it
        # should return a tab which has '/view' appended to the url
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        # Fail if 'view' is used for folder
        self.assertFalse(tabs[-1]["url"][-5:] == "/view")
        # Add Folder to type settings
        registry = getUtility(IRegistry)
        type_settings = registry.forInterface(ITypesSchema, prefix="plone", check=False)
        type_settings.types_use_view_action_in_listings = ["Image", "File", "Folder"]
        # Verify that we have '/view'
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        self.assertEqual(tabs[-1]["url"][-5:], "/view")

    def testTabsExcludeNonFolderishItems(self):
        self.navigation_settings.nonfolderish_tabs = False
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        orig_len = len(tabs)
        self.setRoles(["Manager", "Member"])
        self.portal.invokeFactory("Document", "foo")
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        self.assertEqual(len(tabs), orig_len)

    def testRootBelowPortalRoot(self):
        self.setRoles(["Manager"])
        self.portal.manage_delObjects(["news", "events", "Members"])
        self.setRoles(["Member"])
        self.navigation_settings.nonfolderish_tabs = False
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        self.assertTrue(tabs)
        self.assertEqual(len(tabs), 2)
        self.assertEqual(tabs[0]["id"], "folder1")
        self.assertEqual(tabs[1]["id"], "folder2")

    def testPortalTabsNotIncludeViewNamesInCSSid(self):
        self.setRoles(["Manager"])
        self.portal.invokeFactory("File", "file1")
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        for tab in tabs:
            self.assertEqual(validateCSSIdentifier(tab["id"]), True)

    def testLinkRemoteUrlsUsedUnlessLinkCreator(self):
        self.setRoles(["Manager"])
        self.portal.invokeFactory("Link", "link1")
        self.portal.link1.remoteUrl = "http://plone.org"
        self.portal.link1.reindexObject()
        view = self.view_class(self.portal, self.request)
        tabs = view.topLevelTabs(actions=[])
        for tab in tabs:
            # as Creator tab for link1 should have url of the item
            if tab["id"] == "link1":
                self.assertTrue(tab["url"] == "http://nohost/plone/link1")

        self.setRoles(["Manager"])
        self.portal.link1.setCreators(["some_other_user"])
        self.portal.link1.reindexObject()
        tabs = view.topLevelTabs(actions=[])
        for tab in tabs:
            # as non-Creator user, tab for link1 should have url of the remote
            # url
            if tab["id"] == "link1":
                self.assertTrue(tab["url"] == "http://plone.org")


class TestCatalogPortalTabs(TestBasePortalTabs):
    view_class = CatalogNavigationTabs


class TestBaseBreadCrumbs(PloneTestCase.PloneTestCase):
    """Tests for the portal tabs query"""

    view_class = None

    def afterSetUp(self):
        self.request = self.app.REQUEST
        self.populateSite()
        registry = getUtility(IRegistry)
        self.navigation_settings = registry.forInterface(
            INavigationSchema, prefix="plone"
        )

    def populateSite(self):
        self.setRoles(["Manager"])
        self.portal.invokeFactory("Folder", "folder1")
        folder1 = getattr(self.portal, "folder1")
        folder1.invokeFactory("Document", "doc11")
        folder1.invokeFactory("File", "file11")
        self.setRoles(["Member"])

    def testCreateBreadCrumbs(self):
        # See if we can create one at all
        doc = self.portal.folder1.doc11
        view = self.view_class(doc, self.request)
        crumbs = view.breadcrumbs()
        self.assertTrue(crumbs)
        self.assertEqual(len(crumbs), 2)
        self.assertEqual(crumbs[-1]["absolute_url"], doc.absolute_url())
        self.assertEqual(crumbs[-2]["absolute_url"], doc.aq_parent.absolute_url())

    def testBreadcrumbsRespectTypesWithViewAction(self):
        # With a type in types_use_view_action_in_listings as current action it
        # should return a breadcrumb which has '/view' appended to the url
        view = self.view_class(self.portal.folder1.file11, self.request)
        crumbs = view.breadcrumbs()
        self.assertTrue(crumbs)
        self.assertEqual(crumbs[-1]["absolute_url"][-5:], "/view")

    def testBreadcrumbsStopAtNavigationRoot(self):
        self.navigation_settings.top_level = 1
        self.navigation_settings.root = "/folder1"
        view = self.view_class(self.portal.folder1.doc11, self.request)
        crumbs = view.breadcrumbs()
        self.assertTrue(crumbs)
        self.assertEqual(
            crumbs[0]["absolute_url"], self.portal.folder1.doc11.absolute_url()
        )


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
        self.assertEqual(
            newcrumbs[-1]["absolute_url"], self.portal.folder1.doc11.absolute_url()
        )

    def testBreadcrumbsFilterByInterface2(self):
        # Test url of subfolder of hidden folder.
        self.portal.folder1.invokeFactory("Folder", "subfolder11")
        directlyProvides(self.portal.folder1.subfolder11, IHideFromBreadcrumbs)
        self.portal.folder1.subfolder11.invokeFactory("Folder", "subfolder111")
        self.portal.folder1.subfolder11.subfolder111.invokeFactory(
            "Document", "doc1111"
        )
        doc1111 = self.portal.folder1.subfolder11.subfolder111.doc1111
        view = self.view_class(doc1111, self.request)
        newcrumbs = view.breadcrumbs()
        self.assertEqual(
            newcrumbs[-2]["absolute_url"],
            self.portal.folder1.subfolder11.subfolder111.absolute_url(),
        )


def test_suite():
    import unittest

    return unittest.TestSuite((
        unittest.defaultTestLoader.loadTestsFromTestCase(TestCatalogPortalTabs),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestSiteMap),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestCatalogBreadCrumbs),
        unittest.defaultTestLoader.loadTestsFromTestCase(TestPhysicalBreadCrumbs),
    ))
