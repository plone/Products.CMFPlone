from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component import getUtility

import transaction
import unittest


class TestErrorMessage(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer["request"]

    def test_error_message_3xx(self):
        # Prepare a fake request
        request = self.request.clone()
        request.other["URL"] = "http://nohost/foo"
        # prepare the redirection tool
        storage = getUtility(IRedirectionStorage)
        storage.add("/foo", "/bar")

        try:
            raise NotFound
        except NotFound as exc:
            view = getMultiAdapter((exc, request), name="index.html")
            self.assertIsNone(view())
            self.assertEqual(
                view.request.response.getHeader("Location"), "http://nohost/bar"
            )
            self.assertEqual(view.request.response.getStatus(), 302)

    def test_error_message_4xx(self):
        try:
            raise NotFound
        except NotFound as exc:
            view = getMultiAdapter((exc, self.request.clone()), name="index.html")
            self.assertEqual('{"error_type": "NotFound"}', view())
            self.assertEqual(view.request.response.getStatus(), 404)

    def test_error_message_5xx(self):
        class CustomException(Exception):
            pass

        try:
            raise CustomException
        except CustomException as exc:
            view = getMultiAdapter((exc, self.request.clone()), name="index.html")
            self.assertEqual('{"error_type": "CustomException"}', view())

            # Check the response page (served only when accepting html)
            view.request.environ["HTTP_ACCEPT"] = "text/html"
            self.assertIn("Error", view())
            self.assertEqual(view.request.response.getStatus(), 500)

        # Zope might set a more specific status based on the exception
        try:
            raise KeyError
        except KeyError as exc:
            view = getMultiAdapter((exc, self.request.clone()), name="index.html")
            view()
            self.assertEqual('{"error_type": "KeyError"}', view())

            # Check the response page (served only when accepting html)
            view.request.environ["HTTP_ACCEPT"] = "text/html"
            self.assertIn("Error", view())
            self.assertEqual(view.request.response.getStatus(), 503)


class TestNotFoundBelowPrivateContent(unittest.TestCase):
    """The 404 page below private content must be a complete page.

    https://github.com/plone/Products.CMFPlone/issues/4145
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.portal_workflow.setChainForPortalTypes(
            ["Folder"], "simple_publication_workflow"
        )
        self.portal.invokeFactory("Folder", "private-folder")
        transaction.commit()
        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = True
        self.browser.raiseHttpErrors = False
        self.browser.addHeader("Accept", "text/html")

    def assertCompleteNotFoundPage(self, url):
        self.browser.open(url)
        self.assertEqual(self.browser.headers["status"], "404 Not Found")
        contents = self.browser.contents
        self.assertIn("This page does not seem to exist", contents)
        # Rendered on the site root, not on the private folder.
        self.assertIn('id="portal-logo"', contents)
        self.assertIn('id="portal-searchbox"', contents)
        self.assertIn('id="portal-breadcrumbs"', contents)
        self.assertNotIn("section-private-folder", contents)

    def test_anonymous(self):
        self.assertCompleteNotFoundPage(
            self.portal.absolute_url() + "/private-folder/does-not-exist"
        )

    def test_manager(self):
        # Traversal fails before the user is authenticated,
        # so a Manager gets the same page.
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )
        self.assertCompleteNotFoundPage(
            self.portal.absolute_url() + "/private-folder/does-not-exist"
        )

    def test_nested(self):
        self.portal["private-folder"].invokeFactory("Folder", "sub")
        transaction.commit()
        self.assertCompleteNotFoundPage(
            self.portal.absolute_url() + "/private-folder/sub/does-not-exist"
        )
