#
# Tests for displayContentsTab script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from Products.CMFCore.CMFCorePermissions import ListFolderContents
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from AccessControl.Permissions import copy_or_move

from AccessControl import getSecurityManager
from Products.CMFCore.utils import _checkPermission


class TestDisplayContentsTab(PloneTestCase.PloneTestCase):
    '''For the contents tab to display a user must have the ModifyPortalContent,
       ListFolderContents, and copy_or_move permissions either on the object itself,
       or on its parent object. Yes, all three of 'em.
    '''

    def afterSetUp(self):
        self.parent = self.folder.aq_parent

    def testDisplayContentsTab(self):
        # We should see the tab
        self.failUnless(self.folder.displayContentsTab())

    def testAnonymous(self):
        # Anonymous should not see the tab
        self.logout()
        self.failIf(self.folder.displayContentsTab())

    def testNoListPermission(self):
        # We should not see the tab without ListFolderContents
        self.folder.manage_permission(ListFolderContents, ['Manager'], acquire=0)
        self.failIf(self.folder.displayContentsTab())

    def testNoModifyPermission(self):
        # We should not see the tab without ModifyPortalContent
        self.folder.manage_permission(ModifyPortalContent, ['Manager'], acquire=0)
        self.failIf(self.folder.displayContentsTab())

    def testNoCopyPermission(self):
        # We should not see the tab without copy_or_move
        self.folder.manage_permission(copy_or_move, ['Manager'], acquire=0)
        self.failIf(self.folder.displayContentsTab())

    def testDefaultParentPermissions(self):
        # Note that we don not have ModifyPortalContent in the parent by default!
        self.failIf(_checkPermission(ModifyPortalContent, self.parent))
        self.failUnless(_checkPermission(ListFolderContents, self.parent))
        self.failUnless(_checkPermission(copy_or_move, self.parent))

    def testModifyPermissionInParent(self):
        # We should see the tab once we have all three permissions in the parent
        self.folder.manage_permission(ModifyPortalContent, ['Manager'], acquire=0)
        self.parent.manage_permission(ModifyPortalContent, ['Member'], acquire=1)
        self.failUnless(self.folder.displayContentsTab())

    def testNoListPermissionInParent(self):
        # If we do have ModifyPortalContent in the parent but not
        # ListFolderContents, we should *not* see the tab.
        self.folder.manage_permission(ModifyPortalContent, ['Manager'], acquire=0)
        self.parent.manage_permission(ModifyPortalContent, ['Member'], acquire=1)
        self.parent.manage_permission(ListFolderContents, ['Manager'], acquire=0)
        self.failIf(self.folder.displayContentsTab())

    def testNoCopyPermissionInParent(self):
        # If we do have ModifyPortalContent in the parent but not
        # copy_or_move, we should *not* see the tab.
        self.folder.manage_permission(ModifyPortalContent, ['Manager'], acquire=0)
        self.parent.manage_permission(ModifyPortalContent, ['Member'], acquire=1)
        self.parent.manage_permission(copy_or_move, ['Manager'], acquire=0)
        self.failIf(self.folder.displayContentsTab())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDisplayContentsTab))
    return suite

if __name__ == '__main__':
    framework()
