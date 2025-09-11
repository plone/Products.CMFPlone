from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import unittest


class TestViews(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_resetpassword_view(self):
        view = getMultiAdapter(
            (self.portal, self.request), name="initial-login-password-change"
        )
        self.assertTrue(view())

    def test_loggedout_view(self):
        view = getMultiAdapter((self.portal, self.request), name="logged-out")
        self.assertTrue(view())
