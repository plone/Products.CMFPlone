from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFCore.interfaces import IWorkflowTool
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests.dummy import Dummy
from Products.CMFPlone.tests.dummy import DummyWorkflowChainAdapter
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.interface import directlyProvides
from zope.interface import Interface


default_user = PloneTestCase.default_user


class IDocument(Interface):
    """Dummy document interface"""


class TestWorkflowTool(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.workflow = self.portal.portal_workflow

        self.portal.acl_users._doAddUser("member", TEST_USER_PASSWORD, ["Member"], [])
        self.portal.acl_users._doAddUser(
            "reviewer", TEST_USER_PASSWORD, ["Reviewer"], []
        )
        self.portal.acl_users._doAddUser("manager", TEST_USER_PASSWORD, ["Manager"], [])

        self.folder.invokeFactory("Document", id="doc")
        self.doc = self.folder.doc

        self.folder.invokeFactory("Event", id="ev")
        self.ev = self.folder.ev

    def testGetTransitionsForProvidesURL(self):
        trans = self.workflow.getTransitionsFor(self.doc)
        self.assertEqual(len(trans), 2)
        self.assertTrue("url" in trans[0])
        # Test that url has filled in string substitutions for content url
        self.assertTrue("http://" in trans[0]["url"])

    def testGetTransitionsForProvidesDescription(self):
        trans = self.workflow.getTransitionsFor(self.doc)
        self.assertEqual(len(trans), 2)
        self.assertTrue("description" in trans[0])

    def testGetTitleForStateOnType(self):
        state_id = self.workflow.getInfoFor(self.doc, "review_state", "")
        state_title = self.workflow.getTitleForStateOnType(
            state_id, self.doc.portal_type
        )
        self.assertEqual(state_id, "visible")
        self.assertEqual(state_title.lower(), "public draft")

    def testGetTitleForStateOnTypeFallsBackOnStateId(self):
        state_id = "nonsense"
        state_title = self.workflow.getTitleForStateOnType(
            state_id, self.doc.portal_type
        )
        self.assertEqual(state_title, "nonsense")

    def testGetTitleForStateOnTypeSucceedsWithNonString(self):
        # Related to http://dev.plone.org/plone/ticket/4638
        # Non content objects can pass None or MissingValue.
        state_id = None
        state_title = self.workflow.getTitleForStateOnType(
            state_id, self.doc.portal_type
        )
        self.assertEqual(state_title, state_id)

    def testGetTitleForTransitionOnType(self):
        state_id = "hide"
        state_title = self.workflow.getTitleForTransitionOnType(
            state_id, self.doc.portal_type
        )
        self.assertEqual(state_title, "Make private")

    def testGetTitleForTransitionOnTypeFallsBackOnTransitionId(self):
        state_id = "nonsense"
        state_title = self.workflow.getTitleForTransitionOnType(
            state_id, self.doc.portal_type
        )
        self.assertEqual(state_title, "nonsense")

    def testGetTitleForTransitionOnTypeSucceedsWithNonString(self):
        # Related to http://dev.plone.org/plone/ticket/4638
        # Non content objects can pass None or MissingValue.
        state_id = None
        state_title = self.workflow.getTitleForTransitionOnType(
            state_id, self.doc.portal_type
        )
        self.assertEqual(state_title, state_id)

    def testListWFStatesByTitle(self):
        from Products.CMFPlone.WorkflowTool import WorkflowTool
        from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
        from Products.DCWorkflow.States import StateDefinition

        tool = WorkflowTool()

        # Test without workflows
        self.assertListEqual(tool.listWFStatesByTitle(), [])
        self.assertListEqual(tool.listWFStatesByTitle(filter_similar=True), [])

        # Test with an empty workflow
        tool["foo"] = DCWorkflowDefinition("foo")

        self.assertListEqual(tool.listWFStatesByTitle(), [])
        self.assertListEqual(tool.listWFStatesByTitle(filter_similar=True), [])

        # Test with dummy states
        tool["foo"].states["private"] = StateDefinition("private")
        tool["foo"].states["published"] = StateDefinition("published")

        expected = [
            (
                "",
                "private",
            ),
            ("", "published"),
        ]
        self.assertListEqual(tool.listWFStatesByTitle(), expected)
        self.assertListEqual(tool.listWFStatesByTitle(filter_similar=True), expected)

        # Test with concurrent states
        tool["bar"] = DCWorkflowDefinition("bar")
        tool["bar"].states["private"] = StateDefinition("private")
        tool["bar"].states["pending"] = StateDefinition("pending")
        tool["bar"].states["published"] = StateDefinition("published")
        tool["bar"].states["published"].setProperties(title="Published")
        expected = [
            (
                "",
                "private",
            ),
            ("", "published"),
            (
                "",
                "private",
            ),
            ("", "pending"),
            ("Published", "published"),
        ]
        self.assertListEqual(tool.listWFStatesByTitle(), expected)
        expected = [
            (
                "",
                "private",
            ),
            ("", "published"),
            ("", "pending"),
            ("Published", "published"),
        ]
        self.assertListEqual(tool.listWFStatesByTitle(filter_similar=True), expected)

    def testAdaptationBasedWorkflowOverride(self):
        # We take a piece of dummy content and register a dummy
        # workflow chain adapter for it.
        content = Dummy()
        directlyProvides(content, IDocument)
        provideAdapter(DummyWorkflowChainAdapter, adapts=(IDocument, IWorkflowTool))
        self.assertEqual(self.workflow.getChainFor(content), ("Static Workflow",))
        # undo our registration so we don't break tests
        components = getGlobalSiteManager()
        components.unregisterAdapter(
            DummyWorkflowChainAdapter, required=(IDocument, IWorkflowTool)
        )
