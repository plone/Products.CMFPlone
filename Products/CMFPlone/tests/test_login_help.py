from plone import api
from plone.testing.zope import Browser
from Products.CMFPlone.browser.login.login_help import RequestResetPassword
from Products.CMFPlone.browser.login.login_help import RequestUsername
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import transaction
import unittest


class TestLoginHelp(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]

    def test_view(self):
        view = getMultiAdapter((self.portal, self.request), name="login-help")
        self.assertTrue(view())

    def test_view_form(self):
        form = getMultiAdapter((self.portal, self.request), name="login-help")
        self.assertEqual(form.subforms, [])
        form.update()
        self.assertEqual(len(form.subforms), 2)
        reset_password = form.subforms[0]
        self.assertTrue(isinstance(reset_password, RequestResetPassword))
        self.assertTrue(reset_password())
        request_username = form.subforms[1]
        self.assertTrue(isinstance(request_username, RequestUsername))
        self.assertTrue(request_username())

    def test_view_form_with_emaillogin(self):
        api.portal.set_registry_record("plone.use_email_as_login", True)
        form = getMultiAdapter((self.portal, self.request), name="login-help")
        self.assertEqual(form.subforms, [])
        form.update()
        self.assertEqual(len(form.subforms), 1)
        reset_password = form.subforms[0]
        self.assertTrue(isinstance(reset_password, RequestResetPassword))
        self.assertTrue(reset_password())
        self.assertTrue(form())

    def test_request_reset_password(self):
        form = getMultiAdapter((self.portal, self.request), name="login-help")
        form.update()
        reset_password = form.subforms[0]
        reset_password.handleResetPassword(reset_password, None)
        # the field reset_password is required
        self.assertEqual(reset_password.status, "There were some errors.")
        # reset error message
        reset_password.status = ""

        self.request["form.widgets.reset_password"] = "test"
        reset_password.handleResetPassword(reset_password, None)
        self.assertEqual(reset_password.status, "")
        self.assertEqual(len(self.portal.MailHost.messages), 0)
        # no mail was sent since the user does not exist
        self.request["form.widgets.reset_password"] = "test"

        member = api.user.get("test_user_1_")
        email = "foo@plone.org"
        member.setMemberProperties({"email": email})
        self.request["form.widgets.reset_password"] = "test_user_1_"
        reset_password.handleResetPassword(reset_password, None)
        self.assertEqual(reset_password.status, "")
        self.assertEqual(len(self.portal.MailHost.messages), 1)
        message = self.portal.MailHost.messages[0]
        self.assertIn(b"To: foo@plone.org", message)
        self.assertIn(b"http://nohost/plone/passwordreset/", message)


class TestLoginHelpFunctional(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.browser = Browser(self.layer["app"])

    def test_login_help_request_password_reset(self):
        self.browser.open("http://nohost/plone/login")
        self.browser.getLink("Get help").click()
        self.assertEqual(self.browser.url, "http://nohost/plone/@@login-help")

        member = api.user.get("test_user_1_")
        email = "foo@plone.org"
        member.setMemberProperties({"email": email})
        transaction.commit()
        # validaton error of empty required field
        self.browser.getControl(name="form.buttons.reset").click()
        self.assertEqual(self.browser.url, "http://nohost/plone/@@login-help")

        self.browser.getControl(
            name="form.widgets.reset_password"
        ).value = "nonexistinguser"  # noqa: E501
        self.browser.getControl(name="form.buttons.reset").click()
        self.assertEqual(self.browser.url, "http://nohost/plone/@@login-help")
        # message appears even though no email was sent
        self.assertIn(
            "An email has been sent with instructions on how to reset your password.",  # noqa: E501
            self.browser.contents,
        )
        self.assertEqual(len(self.portal.MailHost.messages), 0)

        self.browser.getControl(
            name="form.widgets.reset_password"
        ).value = "test_user_1_"
        self.browser.getControl(name="form.buttons.reset").click()
        self.assertIn(
            "An email has been sent with instructions on how to reset your password.",  # noqa: E501
            self.browser.contents,
        )
        # message was actually sent
        self.assertEqual(len(self.portal.MailHost.messages), 1)

    def test_login_help_request_username(self):
        self.browser.open("http://nohost/plone/login")
        self.browser.getLink("Get help").click()
        self.assertEqual(self.browser.url, "http://nohost/plone/@@login-help")

        member = api.user.get("test_user_1_")
        email = "foo@plone.org"
        member.setMemberProperties({"email": email})
        transaction.commit()

        # validaton error of empty required field
        self.browser.getControl(name="form.buttons.get_username").click()
        self.assertEqual(self.browser.url, "http://nohost/plone/@@login-help")
        self.assertIn("missing", self.browser.contents)

        self.browser.getControl(
            name="form.widgets.recover_username"
        ).value = "foo@plone.org"
        self.browser.getControl(name="form.buttons.get_username").click()
        self.assertEqual(self.browser.url, "http://nohost/plone/@@login-help")
        # email was sent
        self.assertIn("email has been sent with your username.", self.browser.contents)
        self.assertEqual(len(self.portal.MailHost.messages), 1)
        message = self.portal.MailHost.messages[0]
        self.assertIn(b"To: foo@plone.org", message)
        self.assertIn(b"Your username is: test_user_1_", message)

        self.browser.getControl(name="form.widgets.recover_username").value = "noemail"
        self.browser.getControl(name="form.buttons.get_username").click()
        self.assertIn("specified email is not valid.", self.browser.contents)
        # no new message was sent
        self.assertEqual(len(self.portal.MailHost.messages), 1)

        self.browser.getControl(
            name="form.widgets.recover_username"
        ).value = "bar@plone.org"
        self.browser.getControl(name="form.buttons.get_username").click()
        # no new message was sent
        self.assertIn(
            "email has been sent with your username.",
            self.browser.contents,
        )
        self.assertEqual(len(self.portal.MailHost.messages), 1)

        api.user.create(
            username="another_user_same_email",
            email="foo@plone.org",
            password="password1",
            roles=("Member",),
        )
        transaction.commit()
        self.browser.getControl(
            name="form.widgets.recover_username"
        ).value = "foo@plone.org"
        self.browser.getControl(name="form.buttons.get_username").click()
        # no new message was sent
        self.assertIn(
            "email has been sent with your username.",
            self.browser.contents,
        )
        self.assertEqual(len(self.portal.MailHost.messages), 1)

        api.user.create(
            username="next_user_new_email",
            email="bar@plone.org",
            password="password1",
            roles=("Member",),
        )
        transaction.commit()
        self.browser.getControl(
            name="form.widgets.recover_username"
        ).value = "bar@plone.org"
        self.browser.getControl(name="form.buttons.get_username").click()
        # a message was sent
        self.assertIn(
            "email has been sent with your username.",
            self.browser.contents,
        )
        self.assertEqual(len(self.portal.MailHost.messages), 2)
