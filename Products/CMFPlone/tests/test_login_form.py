from DateTime import DateTime
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.z3cform.interfaces import IPloneFormLayer
from Products.CMFCore.permissions import SetOwnProperties
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import re
import time
import unittest


FORM_ID = "login"


class TestLoginForm(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.mt = getToolByName(self.portal, "portal_membership")
        # suitable for testing z3c.form views
        alsoProvides(self.request, IPloneFormLayer)

    def test_login_view(self):
        view = getMultiAdapter((self.portal, self.request), name="login")
        self.assertTrue(view())

    def _setup_authenticator_request(self):
        self.request.set("REQUEST_METHOD", "POST")
        authenticator = getMultiAdapter(
            (self.portal, self.request), name="authenticator"
        )
        html = authenticator.authenticator()
        token = re.search('value="(.*)"', html).groups()[0]
        self.request.set("_authenticator", token)

    def test_form_update(self):
        self._setup_authenticator_request()
        self.request["__ac_name"] = "test"
        self.request["__ac_password"] = TEST_USER_PASSWORD
        self.request["form.widgets.came_from"] = [""]
        form = self.portal.restrictedTraverse(FORM_ID)
        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

    def test_failsafe_login_form(self):
        view = getMultiAdapter((self.portal, self.request), name="failsafe_login")
        html = view()
        self.assertNotIn("main-container", html)

    def test_failsafe_login_form_update(self):
        self._setup_authenticator_request()
        self.request["__ac_name"] = "test"
        self.request["__ac_password"] = TEST_USER_PASSWORD
        self.request["form.widgets.came_from"] = [""]
        form = self.portal.restrictedTraverse("failsafe_login")
        form.update()
        data, errors = form.extractData()
        self.assertEqual(len(errors), 0)

    def test_login_external(self):
        registry = self.layer["portal"].portal_registry
        registry["plone.external_login_url"] = "http://testurl/extlogin"
        form = self.portal.restrictedTraverse("login")
        form()
        self.assertEqual(
            registry["plone.external_login_url"],
            form.request.response.getHeader("Location"),
        )

    def test_login_external_with_all_params(self):
        registry = self.layer["portal"].portal_registry
        registry["plone.external_login_url"] = "http://testurl/extlogin?level=debug"
        self.request["came_from"] = "foo"
        self.request["next"] = "bar"
        form = self.portal.restrictedTraverse("login")
        form()
        self.assertIn(
            "came_from=foo",
            form.request.response.getHeader("Location"),
        )
        self.assertIn(
            "next=bar",
            form.request.response.getHeader("Location"),
        )
        # Keep the original query string
        self.assertIn(
            "level=debug",
            form.request.response.getHeader("Location"),
        )

    def test_login_external_without_next_param(self):
        registry = self.layer["portal"].portal_registry
        registry["plone.external_login_url"] = "http://testurl/extlogin"
        self.request["came_from"] = "foo"
        form = self.portal.restrictedTraverse("login")
        form()
        self.assertIn(
            "came_from=foo",
            form.request.response.getHeader("Location"),
        )

    def test_failsafe_login_external(self):
        registry = self.layer["portal"].portal_registry
        registry["plone.external_login_url"] = "http://testurl/extlogin"
        form = self.portal.restrictedTraverse("failsafe_login")
        html = form()
        self.assertIsNotNone(html)
        self.assertEqual(None, form.request.response.getHeader("Location"))
        self.assertNotIn("main-container", html)

    def test_login_creates_memberarea(self):
        membership = self.layer["portal"].portal_membership
        form = self.portal.restrictedTraverse("@@login")
        if membership.memberareaCreationFlag == "True":
            self.assertEqual(membership.getHomeFolder(), None)
            form._post_login()
            self.assertNotEqual(membership.getHomeFolder(), None)

    def test_post_login_sets_login_time(self):
        now = DateTime()
        member = self.layer["portal"].portal_membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty("login_time")) < now)
        form = self.portal.restrictedTraverse("@@login")
        form._post_login()
        membership = self.layer["portal"].portal_membership
        member = membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty("login_time")) >= now)

    def test_post_login_sets_last_login_time(self):
        now = DateTime()
        membership = self.layer["portal"].portal_membership
        member = membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty("last_login_time")) < now)
        form = self.portal.restrictedTraverse("@@login")
        form._post_login()
        member = membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty("last_login_time")) >= now)

    def test_post_login_sets_LastLoginTime_if_member_lacks_set_own_properties_permission(
        self,
    ):  # noqa: E501
        # If members lack the "Set own properties" permission, they should
        # still be able to log in, and their login times should be set.
        now = DateTime()
        self.portal.manage_permission(SetOwnProperties, ["Manager"], acquire=0)
        form = self.portal.restrictedTraverse("@@login")
        form._post_login()
        membership = self.layer["portal"].portal_membership
        member = membership.getAuthenticatedMember()
        self.assertTrue(DateTime(member.getProperty("last_login_time")) >= now)

    def test_initial_login_time_does_change(self):
        membership = self.layer["portal"].portal_membership
        member = membership.getAuthenticatedMember()
        form = self.portal.restrictedTraverse("@@login")
        form._post_login()
        member = membership.getAuthenticatedMember()
        login_time = DateTime(member.getProperty("login_time"))
        # Log in again later
        time.sleep(0.2)
        form._post_login()
        # login_time did change
        member = membership.getAuthenticatedMember()
        self.assertTrue(
            DateTime(member.getProperty("login_time")) > login_time,
        )

    def test_initial_login_time_with_string(self):
        membership = self.layer["portal"].portal_membership
        member = membership.getAuthenticatedMember()
        # Realize the login_time is not string but DateTime
        self.assertIsInstance(member.getProperty("login_time"), DateTime)
        self.assertEqual(member.getProperty("login_time").Date(), "2000/01/01")

        # Update login_time into string
        today = DateTime().Date()
        member.setProperties(login_time=today)
        self.assertIsInstance(member.getProperty("login_time"), str)
        self.assertEqual(member.getProperty("login_time"), today)

        # Logging in set login_time with DateTime
        form = self.portal.restrictedTraverse("@@login")
        form._post_login()
        member = membership.getAuthenticatedMember()
        self.assertIsInstance(member.getProperty("login_time"), DateTime)
        self.assertTrue(member.getProperty("login_time") > DateTime(today))
