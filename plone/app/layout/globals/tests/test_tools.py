from plone.app.layout.globals.tests.base import GlobalsTestCase
from Products.CMFPlone.utils import getToolByName


class TestToolsView(GlobalsTestCase):
    """Tests the global tools view.
    """

    def afterSetUp(self):
        self.view = self.folder.restrictedTraverse('@@plone_tools')

    def test_actions(self):
        self.assertEquals(self.view.actions(), getToolByName(self.folder, 'portal_actions'))

    def test_catalog(self):
        self.assertEquals(self.view.catalog(), getToolByName(self.folder, 'portal_catalog'))

    def test_membership(self):
        self.assertEquals(self.view.membership(), getToolByName(self.folder, 'portal_membership'))

    def test_properties(self):
        self.assertEquals(self.view.properties(), getToolByName(self.folder, 'portal_properties'))

    def test_syndication(self):
        self.assertEquals(self.view.syndication(), getToolByName(self.folder, 'portal_syndication'))

    def test_types(self):
        self.assertEquals(self.view.types(), getToolByName(self.folder, 'portal_types'))

    def test_url(self):
        self.assertEquals(self.view.url(), getToolByName(self.folder, 'portal_url'))

    def test_workflow(self):
        self.assertEquals(self.view.workflow(), getToolByName(self.folder, 'portal_workflow'))


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
