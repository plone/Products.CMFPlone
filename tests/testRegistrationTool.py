#
# Tests the registration tool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base

member_id = 'new_member'


class TestRegistrationTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.registration = self.portal.portal_registration

    def testJoinCreatesUser(self):
        self.registration.addMember(member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com'})
        user = self.portal.acl_users.getUserById(member_id)
        self.failUnless(user, 'addMember failed to create user')

    def testJoinWithoutEmailRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          member_id, 'secret',
                          properties={'username': member_id, 'email': ''})


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


if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestRegistrationTool))
        suite.addTest(makeSuite(TestPasswordGeneration))
        return suite
