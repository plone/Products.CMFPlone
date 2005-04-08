#
# Tests the registration tool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base
from AccessControl import Unauthorized
from Products.CMFCore.CMFCorePermissions import AddPortalMember

member_id = 'new_member'


class TestRegistrationTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.registration = self.portal.portal_registration

    def testJoinCreatesUser(self):
        self.registration.addMember(member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com'})
        user = self.portal.acl_users.getUserById(member_id)
        self.failUnless(user, 'addMember failed to create user')

    def testJoinWithUppercaseEmailCreatesUser(self):
        self.registration.addMember(member_id, 'secret',
                          properties={'username': member_id, 'email': 'FOO@BAR.COM'})
        user = self.portal.acl_users.getUserById(member_id)
        self.failUnless(user, 'addMember failed to create user')

    def testJoinWithoutEmailRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          member_id, 'secret',
                          properties={'username': member_id, 'email': ''})

    def testJoinWithBadEmailRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com, fred@bedrock.com'})

    def testJoinAsExistingMemberRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          PloneTestCase.default_user, 'secret',
                          properties={'username': 'Dr FooBar', 'email': 'foo@bar.com'})

    def testJoinAsExistingNonMemberUserRaisesValueError(self):
        # http://plone.org/collector/3221
        self.portal.acl_users._doAddUser(member_id, 'secret', [], [])
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com'})

    def testJoinWithPortalIdAsUsernameRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          self.portal.getId(), 'secret',
                          properties={'username': 'Dr FooBar', 'email': 'foo@bar.com'})

    def testJoinWithoutPermissionRaisesUnauthorized(self):
        # http://plone.org/collector/3000
        self.portal.manage_permission(AddPortalMember, ['Manager'], acquire=0)
        self.assertRaises(Unauthorized,
                          self.registration.restrictedTraverse, 'addMember')

    def testJoinWithoutPermissionRaisesUnauthorizedFormScript(self):
        # http://plone.org/collector/3000
        self.portal.manage_permission(AddPortalMember, ['Manager'], acquire=0)
        self.app.REQUEST['username'] = member_id
        # XXX: register has a proxy role but we trip over
        # validate_registration... (2.0.5)
        self.assertRaises(Unauthorized, self.portal.register)

    def testInvalidCMFDefaultEmailFailsValidation(self):
        # http://plone.org/collector/3910
        self.failIf(self.registration.isValidEmail('bogus@127.0.0.1'))
    

class TestPasswordGeneration(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.registration = self.portal.portal_registration

    def testMD5BaseAttribute(self):
        # Verify that if the _v_md5base attribute is missing, things
        # fall back to the class attribute and its default value.
        self.registration._md5base()
        self.failIfEqual(self.registration._v_md5base, None)
        delattr(self.registration, '_v_md5base')
        self.assertEqual(self.registration._v_md5base, None)

    def testGetRandomPassword(self):
        pw = self.registration.getPassword(6)
        self.assertEqual(len(pw), 6)

    def testGetDeterministicPassword(self):
        salt = 'foo'
        pw = self.registration.getPassword(6, salt)
        self.assertEqual(len(pw), 6)
        # Passing in the same length and salt should give the same
        # result, every time.
        self.assertEqual(pw, self.registration.getPassword(6, salt))
        self.assertEqual(pw, self.registration.getPassword(6, salt))
        # These should fail
        self.failIfEqual(pw, self.registration.getPassword(7, salt))
        self.failIfEqual(pw, self.registration.getPassword(6, salt+'x'))

    def testGeneratePassword(self):
        pw = self.registration.generatePassword()
        self.assertEqual(len(pw), 6)

    def testGenerateResetCode(self):
        salt = 'foo'
        rc = self.registration.generateResetCode(salt)
        self.assertEqual(rc, self.registration.generateResetCode(salt))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRegistrationTool))
    suite.addTest(makeSuite(TestPasswordGeneration))
    return suite

if __name__ == '__main__':
    framework()
