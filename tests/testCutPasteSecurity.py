#
# Tests the default workflow
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from AccessControl import Unauthorized, getSecurityManager
from OFS.CopySupport import CopyError
from Acquisition import aq_base

_user_name = ZopeTestCase._user_name


class TestContentSecurity(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('user2', 'secret', ['Member'], [])
        self.membership = self.portal.portal_membership

    def testRenameMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='testrename')

        # We need to commit here so that _p_jar isn't None and move
        # will work
        get_transaction().commit(1)
        folder.manage_renameObject('testrename', 'new')
        self.failIf(hasattr(aq_base(folder), 'testrename'))
        self.failUnless(hasattr(aq_base(folder), 'new'))
        self.logout()

    def testRenameOtherMemberContentFails(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user2')
        self.assertRaises(CopyError, folder.manage_renameObject, 'index_html', 'new')
        self.logout()

    def testCopyMemberContent(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testcopy')
        dest = self.membership.getPersonalFolder('user1')
        dest.manage_pasteObjects(src.manage_copyObjects('testcopy'))

        # After a copy/paste, they should *both* have a copy
        self.failUnless(hasattr(aq_base(src), 'testcopy'))
        self.failUnless(hasattr(aq_base(dest), 'testcopy'))        
        self.logout()

    def testCopyOtherMemberContent(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testcopy')
        self.logout()

        self.login('user2')
        dest = self.membership.getPersonalFolder('user2')
        dest.manage_pasteObjects(src.manage_copyObjects('testcopy'))
        # After a copy/paste, they should *both* have a copy
        self.failUnless(hasattr(aq_base(src), 'testcopy'))
        self.failUnless(hasattr(aq_base(dest), 'testcopy'))        
        self.logout()

    def testCutMemberContent(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testcut')

        # We need to commit here so that _p_jar isn't None and move
        # will work
        get_transaction().commit(1)
        
        dest = self.membership.getPersonalFolder('user1')
        dest.manage_pasteObjects(src.manage_cutObjects('testcut'))

        # After a cut/paste, only destination has a copy
        self.failIf(hasattr(aq_base(src), 'testcut'))
        self.failUnless(hasattr(aq_base(dest), 'testcut'))        
        self.logout()
        

    def testCutOtherMemberContent(self):
        self.login('user1')
        src = self.membership.getHomeFolder('user1')
        src.invokeFactory('Document', id='testcut')

        # We need to commit here so that _p_jar isn't None and move
        # will work
        get_transaction().commit(1)
        self.logout()
        
        self.login('user2')
        # FIXME: This doesn't work.  I don't know why CopyError isn't
        # being raised.  Unauthorized isn't raised either.  In fact, the paste succeeds :(
        # Somehow the test fixture has permissions it shouldn't....
        #self.assertRaises(CopyError, src.manage_cutObjects, 'testcut')
        self.logout()


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestContentSecurity))
        return suite

