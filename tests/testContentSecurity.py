#
# Tests content security
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from AccessControl import Unauthorized
from Acquisition import aq_base


class TestContentSecurity(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('user2', 'secret', ['Member'], [])
        self.membership = self.portal.portal_membership
        self.createMemberarea('user1')
        self.createMemberarea('user2')

    def testCreateMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')
        self.failUnless(hasattr(aq_base(folder), 'new'))

    def testCreateOtherMemberContentFails(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user2')
        self.assertRaises(Unauthorized, folder.invokeFactory, 'Document', 'new')

    def testCreateRootContentFails(self):
        self.login('user1')
        self.assertRaises(Unauthorized, self.portal.invokeFactory, 'Document', 'new')

    def testDeleteMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')
        folder.manage_delObjects(['new'])
        self.failIf(hasattr(aq_base(folder), 'new'))

    def testDeleteOtherMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')

        self.login('user2')
        folder = self.membership.getHomeFolder('user1')
        self.assertRaises(Unauthorized, folder.manage_delObjects, ['new'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentSecurity))
    return suite

if __name__ == '__main__':
    framework()
