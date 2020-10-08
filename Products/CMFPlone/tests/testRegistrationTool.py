import unittest

from AccessControl import Unauthorized
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFPlone.RegistrationTool import _checkEmail
from Products.CMFPlone.interfaces.controlpanel import IMailSchema, ISiteSchema
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from plone.registry.interfaces import IRegistry
from zope.component import getSiteManager, getUtility

member_id = 'new_member'

try:
    # Python 3
    from email import message_from_bytes
except ImportError:
    # Python 2
    from email import message_from_string as message_from_bytes


class TestRegistrationTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.registration = self.portal.portal_registration
        self.portal.acl_users.userFolderAddUser("userid", "password",
                                                (), (), ())
        self.portal.acl_users._doAddGroup("groupid", ())

    def testJoinCreatesUser(self):
        self.registration.addMember(member_id, 'secret',
                                    properties={'username': member_id,
                                                'email': 'foo@bar.com'})
        user = self.portal.acl_users.getUserById(member_id)
        self.assertTrue(user, 'addMember failed to create user')

    def testCannotRegisterWithRootAdminUsername(self):
        root_user = self.portal.aq_parent.acl_users.users.listUserIds()[0]
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          root_user, 'secret',
                          properties={'username': root_user,
                                      'email': 'foo@bar.com'})

    def testJoinWithUppercaseEmailCreatesUser(self):
        self.registration.addMember(member_id, 'secret',
                                    properties={'username': member_id,
                                                'email': 'FOO@BAR.COM'})
        user = self.portal.acl_users.getUserById(member_id)
        self.assertTrue(user, 'addMember failed to create user')

    def testJoinWithoutEmailRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          member_id, 'secret',
                          properties={'username': member_id, 'email': ''})

    def testJoinWithBadEmailRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          member_id, 'secret',
                          properties={
                              'username': member_id,
                              'email': 'foo@bar.com, fred@bedrock.com'})

    def testJoinAsExistingMemberRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          PloneTestCase.default_user, 'secret',
                          properties={'username': 'Dr FooBar',
                                      'email': 'foo@bar.com'})

    def testJoinAsExistingNonMemberUserRaisesValueError(self):
        # http://dev.plone.org/plone/ticket/3221
        self.portal.acl_users._doAddUser(member_id, 'secret', [], [])
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          member_id, 'secret',
                          properties={'username': member_id,
                                      'email': 'foo@bar.com'})

    def testJoinWithPortalIdAsUsernameRaisesValueError(self):
        self.assertRaises(ValueError,
                          self.registration.addMember,
                          self.portal.getId(), 'secret',
                          properties={'username': 'Dr FooBar',
                                      'email': 'foo@bar.com'})

    def testJoinWithoutPermissionRaisesUnauthorized(self):
        # http://dev.plone.org/plone/ticket/3000
        self.portal.manage_permission(AddPortalMember, ['Manager'], acquire=0)
        self.assertRaises(Unauthorized,
                          self.registration.restrictedTraverse, 'addMember')

    def testTestPasswordValidityConfirm(self):
        # https://dev.plone.org/ticket/13325
        self.assertTrue(self.registration.testPasswordValidity(
            'validpassword', confirm=None) is None)
        self.assertFalse(self.registration.testPasswordValidity(
            'validpassword', confirm='anotherpassword') is None)

    def testTestPasswordValidityPolicy(self):
        self.assertIsNone(self.registration.testPasswordValidity("abcde", confirm=None))
        self.assertEqual(
            self.registration.testPasswordValidity("abcd", confirm=None),
            "Your password must contain at least 5 characters.",
        )
        # Password validity is checked with an empty password
        # to get a nice help message to show for the input field.
        self.assertEqual(
            self.registration.testPasswordValidity("", confirm=None),
            "Minimum 5 characters.",
        )

    def testPasValidation(self):
        self.assertIsNone(self.registration.pasValidation("password", "abcde"))
        self.assertEqual(
            self.registration.pasValidation("password", "abcd"),
            "Your password must contain at least 5 characters.",
        )

    def testNewIdAllowed(self):
        self.assertEqual(self.registration.isMemberIdAllowed('newuser'), 1)

    def testTakenUserId(self):
        self.assertEqual(self.registration.isMemberIdAllowed('userid'), 0)

    def testTakenGroupd(self):
        self.assertEqual(self.registration.isMemberIdAllowed('groupid'), 0)

    def testIsMemberIdAllowedIfSubstringOfExisting(self):
        # http://dev.plone.org/plone/ticket/6396
        self.assertTrue(self.registration.isMemberIdAllowed('useri'))

    def testRegisteredNotify(self):
        # tests email sending on registration
        # First install a fake mailhost utility
        mails = self.portal.MailHost = MockMailHost('MailHost')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mails, IMailHost)
        # Register a user
        self.registration.addMember(member_id, 'secret',
                                    properties={'username': member_id,
                                                'email': 'foo@bar.com'})

        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix='plone')
        site_settings.site_title = 'Tëst Portal'
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mail_settings.email_from_name = 'Tëst Admin'
        mail_settings.email_from_address = 'bar@baz.com'

        # Notify the registered user
        self.registration.registeredNotify(member_id)
        self.assertEqual(len(mails.messages), 1)
        msg = message_from_bytes(mails.messages[0])
        # We get an encoded subject
        self.assertEqual(
            msg['Subject'],
            '=?utf-8?q?User_Account_Information_for_T=C3=ABst_Portal?=')
        # Also a partially encoded from header
        self.assertEqual(msg['From'],
                         '=?utf-8?q?T=C3=ABst_Admin?= <bar@baz.com>')
        self.assertEqual(msg['Content-Type'], 'text/plain; charset="utf-8"')

    def testRegisteredNotifyEncoding(self):
        mails = self.portal.MailHost = MockMailHost('MailHost')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mails, IMailHost)
        # Register a user
        self.registration.addMember(member_id, 'secret',
                                    properties={'username': member_id,
                                                'email': 'foo@bar.com'})
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix='plone')
        site_settings.site_title = 'Test Portal'
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mail_settings.email_from_name = 'Test Admin'
        mail_settings.email_from_address = 'bar@baz.com'

        # Set the portal email encoding
        mail_settings.email_charset = 'us-ascii'

        # Notify the registered user
        self.registration.registeredNotify(member_id)
        self.assertEqual(len(mails.messages), 1)
        msg = message_from_bytes(mails.messages[0])

        # Ensure charset (and thus Content-Type) were set via template
        self.assertEqual(msg['Content-Type'], 'text/plain; charset="us-ascii"')

    def testMailPassword(self):
        # tests email sending for password emails
        # First install a fake mailhost utility
        mails = self.portal.MailHost = MockMailHost('MailHost')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mails, IMailHost)
        # Register a user
        self.registration.addMember(member_id, 'secret',
                                    properties={'username': member_id,
                                                'email': 'foo@bar.com'})

        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix='plone')
        site_settings.site_title = 'Tëst Portal'
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mail_settings.email_from_name = 'Tëst Admin'
        mail_settings.email_from_address = 'bar@baz.com'

        from zope.publisher.browser import TestRequest
        self.registration.mailPassword(member_id, TestRequest())
        self.assertEqual(len(mails.messages), 1)
        msg = message_from_bytes(mails.messages[0])
        # We get an encoded subject
        self.assertEqual(msg['Subject'],
                         '=?utf-8?q?Password_reset_request?=')
        # Also a partially encoded from header
        self.assertEqual(msg['From'],
                         '=?utf-8?q?T=C3=ABst_Admin?= <bar@baz.com>')
        self.assertEqual(msg['Content-Type'], 'text/plain; charset="utf-8"')

    def testMailPasswordEncoding(self):
        # tests email sending for password emails
        # First install a fake mailhost utility
        mails = self.portal.MailHost = MockMailHost('MailHost')
        sm = getSiteManager(self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mails, IMailHost)
        # Register a user
        self.registration.addMember(member_id, 'secret',
                                    properties={'username': member_id,
                                                'email': 'foo@bar.com'})
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix='plone')
        site_settings.site_title = 'Tëst Portal'
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mail_settings.email_from_name = 'Test Admin'
        mail_settings.email_from_address = 'bar@baz.com'

        # Set the portal email encoding
        mail_settings.email_charset = 'us-ascii'

        from zope.publisher.browser import TestRequest
        self.registration.mailPassword(member_id, TestRequest())
        self.assertEqual(len(mails.messages), 1)
        msg = message_from_bytes(mails.messages[0])

        # Ensure charset (and thus Content-Type) were set via template
        self.assertEqual(msg['Content-Type'], 'text/plain; charset="us-ascii"')


class TestPasswordGeneration(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.registration = self.portal.portal_registration

    def testMD5BaseAttribute(self):
        # Verify that if the _v_md5base attribute is missing, things
        # fall back to the class attribute and its default value.
        self.registration._md5base()
        self.assertNotEqual(self.registration._v_md5base, None)
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
        self.assertNotEqual(pw, self.registration.getPassword(7, salt))
        self.assertNotEqual(pw, self.registration.getPassword(6, salt + 'x'))

    def testGeneratePassword(self):
        pw = self.registration.generatePassword()
        # default password is now very long as it's never seen by the user
        self.assertTrue(len(pw) >= 20)

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
        result = self.check("webmaster@example.xn--wgbh1c")
        self.assertTrue(*result)

    def test_long_tld(self):
        result = self.check("webmaster@example.onion")
        self.assertTrue(*result)


class TestRegistrationToolEmailValidityChecker(PloneTestCase.PloneTestCase):

    check = lambda _, email: _.portal.portal_registration.isValidEmail(email)
