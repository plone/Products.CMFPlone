from Acquisition import aq_base
from Products.CMFPlone.tests import PloneTestCase


class TestPloneTestCase(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.setupAuthenticator()

    def testAddDocument(self):
        self.assertFalse(self.catalog(id="new"))
        self.folder.invokeFactory("Document", id="new")
        self.assertTrue(hasattr(aq_base(self.folder), "new"))
        self.assertTrue(self.catalog(id="new"))

    def testPublishDocument(self):
        self.folder.invokeFactory("Document", id="new")
        self.setRoles(["Reviewer"])
        self.workflow.doActionFor(self.folder.new, "publish")
        self.assertEqual(
            self.workflow.getInfoFor(self.folder.new, "review_state"), "published"
        )
        self.assertTrue(self.catalog(id="new", review_state="published"))

    def testRetractDocument(self):
        self.folder.invokeFactory("Document", id="new")
        self.setRoles(["Reviewer"])
        self.workflow.doActionFor(self.folder.new, "publish")
        self.assertEqual(
            self.workflow.getInfoFor(self.folder.new, "review_state"), "published"
        )
        self.setRoles(["Member"])
        self.workflow.doActionFor(self.folder.new, "retract")
        self.assertEqual(
            self.workflow.getInfoFor(self.folder.new, "review_state"), "visible"
        )
