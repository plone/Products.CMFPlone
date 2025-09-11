from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class NoGopipTests(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

        folder = self.portal[self.portal.invokeFactory("Folder", "foo")]
        subfolder = folder[folder.invokeFactory("Folder", "sub")]
        folder.invokeFactory("Document", id="bar2")
        folder.invokeFactory("Document", id="bar1")
        folder.invokeFactory("Document", id="bar3")
        folder.invokeFactory("Document", id="bar4")
        subfolder.invokeFactory("Document", id="bar5")

    def query(self, **kw):
        return [
            brain.getId
            for brain in self.portal.portal_catalog(
                sort_on="getObjPositionInParent", **kw
            )
        ]

    def testGetObjPositionInParentIndex(self):
        from plone.folder.nogopip import GopipIndex

        catalog = self.portal.portal_catalog
        self.assertIn("getObjPositionInParent", catalog.indexes())
        self.assertIsInstance(catalog.Indexes["getObjPositionInParent"], GopipIndex)

    def testSearchOneFolder(self):
        ids = self.query(path=dict(query="/plone/foo", depth=1))
        self.assertEqual(ids, ["sub", "bar2", "bar1", "bar3", "bar4"])

    def testSortDocumentsInFolder(self):
        ids = self.query(path=dict(query="/plone/foo", depth=1), Type="Page")
        self.assertEqual(ids, ["bar2", "bar1", "bar3", "bar4"])

    def testSortDocumentsInTree(self):
        ids = self.query(path="/plone/foo", Type="Page")
        self.assertEqual(ids, ["bar5", "bar2", "bar1", "bar3", "bar4"])
