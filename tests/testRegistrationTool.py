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

    def testMD5Base(self):
        # Verify that if the _v_md5base attribute is missing things
        # fall back to the class attribute and its default value.
        self.registration._md5base()
        self.failIfEqual(self.registration._v_md5base, None)
        delattr(self.registration, '_v_md5base')
        self.assertEqual(self.registration._v_md5base, None)

    def testGetRandomPassword(self):
        pw = self.registration.getPassword(6)
        self.assertEqual(len(pw), 6)

    def testGetDeterministicPassword(self):
        # I am not qualified to write this test, geoffd?
        s = 'some hash'
        pw = self.registration.getPassword(6, s)
        self.assertEqual(len(pw), 6)
        # Now what qualities should the pw have?
        # ...

 
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestRegistrationTool))
        suite.addTest(unittest.makeSuite(TestPasswordGeneration))
        return suite

