from AccessControl import Unauthorized
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.base.interfaces import ISecuritySchema
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.utils import set_own_login_name
from zope.component import getUtility


class TestEmailLogin(PloneTestCase.PloneTestCase):
    def testUseEmailSetting(self):
        registry = getUtility(IRegistry)
        security_settings = registry.forInterface(ISecuritySchema, prefix="plone")

        self.assertFalse(security_settings.use_email_as_login)

    def testSetOwnLoginName(self):
        memship = self.portal.portal_membership
        users = self.portal.acl_users.source_users
        member = memship.getAuthenticatedMember()
        self.assertEqual(
            users.getLoginForUserId(PloneTestCase.default_user), "test-user"
        )
        set_own_login_name(member, "maurits")
        self.assertEqual(users.getLoginForUserId(PloneTestCase.default_user), "maurits")

    def testSetLoginNameOfOther(self):
        memship = self.portal.portal_membership
        memship.addMember("maurits", TEST_USER_PASSWORD, [], [])
        member = memship.getMemberById("maurits")
        with self.assertRaises(Unauthorized):
            set_own_login_name(member, "vanrees")
        # The admin *should* be able to change the login name of
        # another user.  See http://dev.plone.org/plone/ticket/11255
        self.loginAsPortalOwner()
        set_own_login_name(member, "vanrees")
        users = self.portal.acl_users.source_users
        self.assertEqual(users.getLoginForUserId("maurits"), "vanrees")

    def testAdminSetOwnLoginName(self):
        memship = self.portal.portal_membership
        self.loginAsPortalOwner()
        member = memship.getAuthenticatedMember()
        # We are not allowed to change a user at the root zope level.
        # A KeyError is raised, or possibly in later Plone versions a
        # ValueError, so we simply go for an Exception.
        with self.assertRaises(Exception):
            set_own_login_name(member, "vanrees")

    def testNormalMemberIdsAllowed(self):
        pattern = self.portal.portal_registration._ALLOWED_MEMBER_ID_PATTERN
        self.assertTrue(pattern.match("maurits"))
        self.assertTrue(pattern.match("Maur1ts"))
        self.assertTrue(pattern.match("maurits76"))
        self.assertTrue(pattern.match("MAURITS"))

    def testEmailMemberIdsAllowed(self):
        registry = getUtility(IRegistry)
        security_settings = registry.forInterface(ISecuritySchema, prefix="plone")
        security_settings.use_email_as_login = True

        registration = getToolByName(self.portal, "portal_registration")
        pattern = self.portal.portal_registration._ALLOWED_MEMBER_ID_PATTERN
        # Normal user ids are still allowed, even when using the email
        # address as login name.
        self.assertTrue(pattern.match("joe"))
        self.assertTrue(registration.isMemberIdAllowed("joe"))
        # Some normal email addresses
        self.assertTrue(pattern.match("user@example.org"))
        self.assertTrue(registration.isMemberIdAllowed("user@example.org"))
        self.assertTrue(pattern.match("user123@example.org"))
        self.assertTrue(registration.isMemberIdAllowed("user123@example.org"))
        self.assertTrue(pattern.match("user.name@example.org"))
        self.assertTrue(registration.isMemberIdAllowed("user.name@example.org"))
        # Strange, but valid as id:
        self.assertTrue(pattern.match("no.address@example"))
        self.assertTrue(registration.isMemberIdAllowed("no.address@example"))
        # http://dev.plone.org/ticket/11616 mentions some non-standard
        # email addresses.
        # A plus sign in the id gives problems in some parts of the
        # UI, so we do not allow it.
        self.assertFalse(pattern.match("user+test@example.org"))
        self.assertFalse(registration.isMemberIdAllowed("user+test@example.org"))
        # An apostrophe also sounds like a bad idea to use in an id,
        # though this is a valid email address:
        self.assertFalse(pattern.match("o'hara@example.org"))
        self.assertFalse(registration.isMemberIdAllowed("o'hara@example.org"))

    def _add_email_user(self, user_id, email):
        # This is how plone.app.users does it in register.py
        registration = getToolByName(self.portal, "portal_registration")
        registration.addMember(
            user_id,
            TEST_USER_PASSWORD,
        )
        pas = getToolByName(self.portal, "acl_users")
        pas.updateLoginName(user_id, email)

    def test_principal_id_or_login_name_exists_with_emails(self):
        registry = getUtility(IRegistry)
        security_settings = registry.forInterface(ISecuritySchema, prefix="plone")
        security_settings.use_email_as_login = True
        registration = getToolByName(self.portal, "portal_registration")
        user_exists = registration.principal_id_or_login_name_exists

        self.assertFalse(user_exists("maurits"))
        self.assertFalse(user_exists("maurits@example.org"))
        self._add_email_user("maurits", "maurits@example.org")
        self.assertTrue(user_exists("maurits"))
        self.assertTrue(user_exists("maurits@example.org"))

        # A plus sign in the id gives problems in some parts of the
        # UI, so we do not allow it.  But it is fine as login name
        self.assertFalse(user_exists("plus"))
        self.assertFalse(user_exists("user+test@example.org"))
        self._add_email_user("plus", "user+test@example.org")
        self.assertTrue(user_exists("plus"))
        self.assertTrue(user_exists("user+test@example.org"))

        # An apostrophe also sounds like a bad idea to use in an id,
        # but again this is a valid email address:
        self.assertFalse(user_exists("apostrophe"))
        self.assertFalse(user_exists("o'hara@example.org"))
        self._add_email_user("apostrophe", "o'hara@example.org")
        self.assertTrue(user_exists("apostrophe"))
        self.assertTrue(user_exists("o'hara@example.org"))

    def test_get_member_by_login_name(self):
        memship = self.portal.portal_membership
        context = self.portal
        member = memship.getMemberById(PloneTestCase.default_user)

        # Login name and user name start out the same
        found = get_member_by_login_name(context, PloneTestCase.default_user)
        self.assertEqual(member.id, found.id)

        # Change the login name:
        set_own_login_name(member, "vanrees")
        # A member with this user name is still returned:
        found = get_member_by_login_name(context, PloneTestCase.default_user)
        self.assertEqual(member.id, found.id)
        # With the changed login name we can find the member:
        found = get_member_by_login_name(context, "vanrees")
        self.assertEqual(member.id, found.id)

        # Demonstrate that we can find other members than just the
        # default user:
        found = get_member_by_login_name(context, SITE_OWNER_NAME)
        member = memship.getMemberById(SITE_OWNER_NAME)
        self.assertEqual(member.id, found.id)

        # And try one with an actual email address as login name:
        self._add_email_user("arthur", "arthur@dent.example.org")
        found = get_member_by_login_name(context, "arthur@dent.example.org")
        member = memship.getMemberById("arthur")
        self.assertEqual(member.id, found.id)
