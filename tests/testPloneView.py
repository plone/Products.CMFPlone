#
# Test methods used to make ...
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.component import getView

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase import dummy
PloneTestCase.setupPloneSite()

from Products.CMFPlone.utils import _createObjectByType

from Products.CMFPlone.URLTool import URLTool
from Products.CMFPlone.MembershipTool import MembershipTool
from Products.CMFPlone.GroupsTool import GroupsTool
from Products.CMFPlone.GroupDataTool import GroupDataTool
from Products.CMFPlone.ActionsTool import ActionsTool
from Products.CMFPlone.ActionIconsTool import ActionIconsTool

from Products.CMFCore.WorkflowTool import WorkflowTool

from Products.CMFPlone.InterfaceTool import InterfaceTool
from Products.CMFPlone.SyndicationTool import SyndicationTool

class TestPloneView(PloneTestCase.PloneTestCase):
    """Tests the global plone view.  """

    def afterSetUp(self):
        self.view = getView(self.portal, 'plone', self.app.REQUEST)
        self.view._initializeData()

    def testUTool(self):
        assert isinstance(self.view.utool, URLTool)

    def testPortal(self):
        assert self.view.portal == self.portal
        
    def testPortalObject(self):
        assert self.view.portal_object == self.portal

    def testPortalURL(self):
        assert isinstance(self.view.portal_url, type(''))

    def testMTool(self):
        assert isinstance(self.view.mtool, MembershipTool)

    def testGTool(self):
        assert isinstance(self.view.gtool, GroupsTool)

    def testGDTool(self):
        assert isinstance(self.view.gdtool, GroupDataTool)

    def testATool(self):
        assert isinstance(self.view.atool, ActionsTool)

    def testAITool(self):
        assert isinstance(self.view.aitool, ActionIconsTool)

    def testPUtils(self):
        pass

    def testWTool(self):
        assert isinstance(self.view.wtool, WorkflowTool)

    def testIFaceTool(self):
        assert isinstance(self.view.ifacetool, InterfaceTool)

    def testSynTool(self):
        assert isinstance(self.view.syntool, SyndicationTool)

    def testPortalTitle(self):
        pass
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneView))
    return suite

if __name__ == '__main__':
    framework()
