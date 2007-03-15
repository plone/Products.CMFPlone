import unittest
from plone.app.layout.globals.tests.base import GlobalsTestCase

from zope.component import getUtility

from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IURLTool
from Products.CMFCore.interfaces import IConfigurableWorkflowTool


class TestToolsView(GlobalsTestCase):
    """Ensure that the basic redirector setup is successful.
    """
    
    def afterSetUp(self):
        self.view = self.folder.restrictedTraverse('@@plone_tools')
    
    def test_actions(self):
        self.assertEquals(self.view.actions(), getUtility(IActionsTool))
        
    def test_catalog(self):
        self.assertEquals(self.view.catalog(), getUtility(ICatalogTool))
        
    def test_membership(self):
        self.assertEquals(self.view.membership(), getUtility(IMembershipTool))
        
    def test_properties(self):
        self.assertEquals(self.view.properties(), getUtility(IPropertiesTool))
        
    def test_syndication(self):
        self.assertEquals(self.view.syndication(), getUtility(ISyndicationTool))
        
    def test_types(self):
        self.assertEquals(self.view.types(), getUtility(ITypesTool))
        
    def test_url(self):
        self.assertEquals(self.view.url(), getUtility(IURLTool))

    def test_workflow(self):
        self.assertEquals(self.view.workflow(), getUtility(IConfigurableWorkflowTool))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestToolsView))
    return suite
