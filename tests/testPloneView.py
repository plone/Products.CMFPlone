#
# Test methods used to make ...
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.interfaces.NonStructuralFolder import \
     INonStructuralFolder as z2INonStructuralFolder
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
    """Tests the global plone view.  All the old global_defines should be
       in the _data mapping of the view, which is globablized into
       calling templates."""

    def afterSetUp(self):
        # We need to fiddle the request for zope 2.9+
        try:
            from zope.app.publication.browser import setDefaultSkin
            setDefaultSkin(self.app.REQUEST)
        except ImportError:
            # BBB: zope 2.8
            pass
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        self.view = Plone(self.portal, self.app.REQUEST)
        self.view._initializeData()

    def testUTool(self):
        assert isinstance(self.view._data['utool'], URLTool)

    def testPortal(self):
        assert self.view._data['portal'] == self.portal

    def testPortalObject(self):
        assert self.view._data['portal_object'] == self.portal

    def testPortalURL(self):
        assert isinstance(self.view._data['portal_url'], type(''))

    def testMTool(self):
        assert isinstance(self.view._data['mtool'], MembershipTool)

    def testGTool(self):
        assert isinstance(self.view._data['gtool'], GroupsTool)

    def testGDTool(self):
        assert isinstance(self.view._data['gdtool'], GroupDataTool)

    def testATool(self):
        assert isinstance(self.view._data['atool'], ActionsTool)

    def testAITool(self):
        assert isinstance(self.view._data['aitool'], ActionIconsTool)

    def testPUtils(self):
        pass

    def testWTool(self):
        assert isinstance(self.view._data['wtool'], WorkflowTool)

    def testIFaceTool(self):
        assert isinstance(self.view._data['ifacetool'], InterfaceTool)

    def testSynTool(self):
        assert isinstance(self.view._data['syntool'], SyndicationTool)

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

    def testIsStructuralFolderWithZ2NonStructuralFolder(self):
        f = dummy.Folder('z2_nsFolder')
        f.__implements__ = f.__implements__ + (z2INonStructuralFolder,)
        self.failIf(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsDefaultPageInFolder(self):
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failIf(view.isDefaultPageInFolder())
        self.failUnless(self.folder.canSelectDefaultPage())
        self.folder.saveDefaultPage('test')
        # re-create the view, because the old value is cached
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failUnless(view.isDefaultPageInFolder())

    def testNavigationRootPath(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootPath(), self.portal.portal_url.getPortalPath())

    def testNavigationRootUrl(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootUrl(), self.portal.absolute_url())

    def testGetParentObject(self):
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertEqual(view.getParentObject(), self.folder)
        # Make sure this looks only at containment
        view = Plone(self.folder.test.__of__(self.portal), self.app.REQUEST)
        self.assertEqual(view.getParentObject(), self.folder)

    def testIsFolderOrFolderDefaultPage(self):
        # an actual folder whould return true
        view = Plone(self.folder, self.app.REQUEST)
        self.failUnless(view.isFolderOrFolderDefaultPage())
        # But not a document
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failIf(view.isFolderOrFolderDefaultPage())
        # Unless we make it the default view
        self.folder.saveDefaultPage('test')
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failUnless(view.isFolderOrFolderDefaultPage())
        # And if we have a non-structural folder it should not be true
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        view = Plone(self.folder.ns_folder, self.app.REQUEST)
        self.failIf(view.isFolderOrFolderDefaultPage())

    def testIsPortalOrPortalDefaultPage(self):
        # an actual folder whould return true
        view = Plone(self.portal, self.app.REQUEST)
        self.failUnless(view.isPortalOrPortalDefaultPage())
        # But not a document
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'portal_test',
                                  title='Test default page')
        view = Plone(self.portal.portal_test, self.app.REQUEST)
        self.failIf(view.isPortalOrPortalDefaultPage())
        # Unless we make it the default view
        self.portal.saveDefaultPage('portal_test')
        view = Plone(self.portal.portal_test, self.app.REQUEST)
        self.failUnless(view.isPortalOrPortalDefaultPage())

    def testGetCurrentFolder(self):
        # If context is a folder, then the folder is returned
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)
        # If context is not a folder, then the parent is returned
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)
        # The real container is returned regardless of context
        view = Plone(self.folder.test.__of__(self.portal), self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)
        # A non-structural folder does not count as a folder`
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        view = Plone(self.folder.ns_folder, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)
        # And even a structural folder that is used as a default page
        # returns its parent
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Topic', 'topic')
        view = Plone(self.folder.topic, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder.topic)
        self.folder.saveDefaultPage('topic')
        view = Plone(self.folder.topic, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)


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
