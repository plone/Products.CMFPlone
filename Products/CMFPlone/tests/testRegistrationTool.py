#
# Tests the registration tool
#
import unittest

from email import message_from_string
from zope.component import getSiteManager
from Products.CMFPlone.tests import PloneTestCase

from AccessControl import Unauthorized
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from Products.CMFPlone.RegistrationTool import _checkEmail

member_id = 'new_member'


class TestRegistrationTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.registration = self.portal.portal_registration
        self.portal.acl_users.userFolderAddUser("userid", "password",
                (), (), ())
        self.portal.acl_users._doAddGroup("groupid", ())

    def testJoinCreatesUser(self):
        self.registration.addMember(member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com'})
        user = self.portal.acl_users.getUserById(member_id)
        self.failUnless(user, 'addMember failed to create user')

    def testCannotRegisterWithRootAdminUsername(self):
        root_user = self.portal.aq_parent.acl_users.users.listUserIds()[0]
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          root_user, 'secret',
                          properties={'username': root_user, 'email': 'foo@bar.com'})

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
        # http://dev.plone.org/plone/ticket/3221
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
        # http://dev.plone.org/plone/ticket/3000
        self.portal.manage_permission(AddPortalMember, ['Manager'], acquire=0)
        self.assertRaises(Unauthorized,
                          self.registration.restrictedTraverse, 'addMember')

    def testNewIdAllowed(self):
        self.assertEqual(self.registration.isMemberIdAllowed('newuser'), 1)


    def testTakenUserId(self):
        self.assertEqual(self.registration.isMemberIdAllowed('userid'), 0)


    def testTakenGroupd(self):
        self.assertEqual(self.registration.isMemberIdAllowed('groupid'), 0)

    def testIsMemberIdAllowedIfSubstringOfExisting(self):
        # http://dev.plone.org/plone/ticket/6396
        self.failUnless(self.registration.isMemberIdAllowed('useri'))

    def testRegisteredNotify(self):
        # tests email sending on registration
        # First install a fake mailhost utility
        mails = self.portal.MailHost = MockMailHost('MailHost')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mails, IMailHost)
        # Register a user
        self.registration.addMember(member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com'})
        # Set the portal email info
        self.portal.setTitle('T\xc3\xa4st Portal')
        self.portal.email_from_name = 'T\xc3\xa4st Admin'
        self.portal.email_from_address = 'bar@baz.com'
        self.registration.registeredNotify(member_id)
        self.assertEqual(len(mails.messages), 1)
        msg = message_from_string(mails.messages[0])
        # We get an encoded subject
        self.assertEqual(msg['Subject'],
                         '=?utf-8?q?User_Account_Information_for_T=C3=A4st_Portal?=')
        # Also a partially encoded from header
        self.assertEqual(msg['From'],
                         '=?utf-8?q?T=C3=A4st_Admin?= <bar@baz.com>')
        self.assertEqual(msg['Content-Type'], 'text/plain; charset="utf-8"')
        # And a Quoted Printable encoded body
        self.failUnless('T=C3=A4st Admin' in msg.get_payload())

    def testMailPassword(self):
        # tests email sending for password emails
        # First install a fake mailhost utility
        mails = self.portal.MailHost = MockMailHost('MailHost')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mails, IMailHost)
        # Register a user
        self.registration.addMember(member_id, 'secret',
                          properties={'username': member_id, 'email': 'foo@bar.com'})
        # Set the portal email info
        self.portal.setTitle('T\xc3\xa4st Portal')
        self.portal.email_from_name = 'T\xc3\xa4st Admin'
        self.portal.email_from_address = 'bar@baz.com'
        self.registration.mailPassword(member_id, self.app['REQUEST'])
        self.assertEqual(len(mails.messages), 1)
        msg = message_from_string(mails.messages[0])
        # We get an encoded subject
        self.assertEqual(msg['Subject'],
                         '=?utf-8?q?Password_reset_request?=')
        # Also a partially encoded from header
        self.assertEqual(msg['From'],
                         '=?utf-8?q?T=C3=A4st_Admin?= <bar@baz.com>')
        self.assertEqual(msg['Content-Type'], 'text/plain; charset="utf-8"')
        # And a Quoted Printable encoded body
        self.failUnless('T=C3=A4st Porta' in msg.get_payload())


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

class TestEmailValidityChecker(unittest.TestCase):

    check = lambda _, email: _checkEmail(email)

    def test_generic_tld(self):
        result = self.check("webmaster@example.org")
        self.assertTrue(*result)

    def test_normal_cc_tld(self):
        result = self.check("webmaster@example.co.uk")
        self.assertTrue(*result)

    def test_idn_cc_tld(self):
        result = self.check(u"webmaster@example.xn--wgbh1c")
        self.assertTrue(*result)

    def test_long_tld(self):
        result = self.check(u"webmaster@example.onion")
        self.assertTrue(*result)

class TestRegistrationToolEmailValidityChecker(PloneTestCase.PloneTestCase):

    check = lambda _, email: _.portal.portal_registration.isValidEmail(email)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRegistrationTool))
    suite.addTest(makeSuite(TestPasswordGeneration))
    suite.addTest(makeSuite(TestEmailValidityChecker))
    suite.addTest(makeSuite(TestRegistrationToolEmailValidityChecker))
    return suite
