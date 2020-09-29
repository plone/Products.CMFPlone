from plone.app.redirector.interfaces import IRedirectionStorage
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zExceptions import HTTPNotImplemented
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.component import getUtility

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
