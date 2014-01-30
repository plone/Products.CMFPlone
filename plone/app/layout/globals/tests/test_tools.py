from plone.app.layout.globals.tests.base import GlobalsTestCase
from Products.CMFPlone.utils import getToolByName


class TestToolsView(GlobalsTestCase):
    """Tests the global tools view.
    """

    def afterSetUp(self):
        self.view = self.folder.restrictedTraverse('@@plone_tools')

    def test_actions(self):
        self.assertEqual(self.view.actions(), getToolByName(
            self.folder, 'portal_actions'))

    def test_catalog(self):
        self.assertEqual(self.view.catalog(), getToolByName(
            self.folder, 'portal_catalog'))

    def test_membership(self):
        self.assertEqual(self.view.membership(), getToolByName(
            self.folder, 'portal_membership'))

    def test_properties(self):
        self.assertEqual(self.view.properties(), getToolByName(
            self.folder, 'portal_properties'))

    def test_types(self):
        self.assertEqual(self.view.types(), getToolByName(
            self.folder, 'portal_types'))

    def test_url(self):
        self.assertEqual(self.view.url(), getToolByName(
            self.folder, 'portal_url'))

    def test_workflow(self):
        self.assertEqual(self.view.workflow(), getToolByName(
            self.folder, 'portal_workflow'))
