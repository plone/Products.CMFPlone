from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter

import unittest


class ErrorLogControlPanelFunctionalTest(unittest.TestCase):
    """Test for Controlpanel Error Log"""

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
    error_log_properties = None

    def setUp(self):
        self.app = self.layer["app"]
        self.request = self.layer["request"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        # keep initial error_log_properties to reset them
        self.error_log_properties = self.portal.error_log.getProperties()

        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )

    def tearDown(self):
        # reset error log properties
        keep_entries = self.error_log_properties["keep_entries"]
        copy_to_zlog = self.error_log_properties["copy_to_zlog"]
        ignored_exceptions = self.error_log_properties["ignored_exceptions"]
        self.portal.error_log.setProperties(
            keep_entries, copy_to_zlog, ignored_exceptions
        )

    def test_error_log_control_panel_link(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink("Errors").click()

        self.assertEqual(self.browser.url, "%s/@@error-log-form" % self.portal_url)
        self.assertIn("<h1>Error log</h1>", self.browser.contents)

    def test_error_log_set_properties(self):
        self.assertEqual(self.error_log_properties["keep_entries"], 20)
        self.assertEqual(self.error_log_properties["copy_to_zlog"], True)
        self.assertEqual(
            self.error_log_properties["ignored_exceptions"],
            ("Unauthorized", "NotFound", "Redirect"),
        )

        self.request.form = {
            "keep_entries": 40,
            "ignored_exceptions": ["NotFound", "Redirect"],
        }

        set_properties_view = getMultiAdapter(
            (self.portal, self.request), name="error-log-set-properties"
        )
        set_properties_view()

        error_log_properties = self.portal.error_log.getProperties()
        self.assertEqual(error_log_properties["keep_entries"], 40)
        self.assertEqual(error_log_properties["copy_to_zlog"], False)
        self.assertEqual(
            error_log_properties["ignored_exceptions"], ("NotFound", "Redirect")
        )
