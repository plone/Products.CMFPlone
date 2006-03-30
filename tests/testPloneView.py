#
# Test methods used to make ...
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

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
from Products.CMFPlone.browser.plone import Plone


class TestPloneView(PloneTestCase.PloneTestCase):
    """Tests the global plone view.  """

    def afterSetUp(self):
        self.view = Plone(self.portal, self.app.REQUEST)
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

    def testIsStructuralFolderWithNonFolder(self):
        i = dummy.Item()
        self.failIf(Plone(i, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithFolder(self):
        f = dummy.Folder('struct_folder')
        self.failUnless(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithNonStructuralFolder(self):
        f = dummy.NonStructuralFolder('ns_folder')
        self.failIf(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsDefaultPageInFolder(self):
        # We need to fiddle the request for zope 2.9+
        try:
            from zope.app.publication.browser import setDefaultSkin
            setDefaultSkin(self.app.REQUEST)
        except ImportError:
            # BBB: zope 2.8
            pass
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failIf(view.isDefaultPageInFolder())
        self.failUnless(self.folder.canSelectDefaultPage())
        self.folder.saveDefaultPage('test')
        self.failUnless(view.isDefaultPageInFolder())

    def testNavigationRootPath(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootPath(), self.portal.portal_url.getPortalPath())
        
    def testNavigationRootUrl(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootUrl(), self.portal.absolute_url())

class TestVisibleIdsEnabled(PloneTestCase.PloneTestCase):
    '''Tests the visibleIdsEnabled method'''

    def afterSetUp(self):
        self.view = Plone(self.portal, self.app.REQUEST)
        self.member = self.portal.portal_membership.getAuthenticatedMember()
        self.props = self.portal.portal_properties.site_properties

    def testFailsWithSitePropertyDisabled(self):
        # Set baseline
        self.member.setProperties(visible_ids=False)
        self.props.manage_changeProperties(visible_ids=False)
        # Should fail when site property is set false
        self.failIf(self.view.visibleIdsEnabled())
        self.member.setProperties(visible_ids=True)
        self.failIf(self.view.visibleIdsEnabled())

    def testFailsWithMemberPropertyDisabled(self):
        # Should fail when member property is false
        self.member.setProperties(visible_ids=False)
        self.props.manage_changeProperties(visible_ids=True)
        self.failIf(self.view.visibleIdsEnabled())

    def testSucceedsWithMemberAndSitePropertyEnabled(self):
        # Should succeed only when site property and member property are true
        self.props.manage_changeProperties(visible_ids=True)
        self.member.setProperties(visible_ids=True)
        self.failUnless(self.view.visibleIdsEnabled())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneView))
    suite.addTest(makeSuite(TestVisibleIdsEnabled))
    return suite

if __name__ == '__main__':
    framework()
