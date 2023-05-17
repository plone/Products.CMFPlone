from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IDateAndTimeSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class DateAndTimeRegistryIntegrationTest(unittest.TestCase):
    """Test date and time related settings."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_controlpanel_schema(self):
        self.assertTrue("portal_timezone" in IDateAndTimeSchema.names())
        self.assertTrue("available_timezones" in IDateAndTimeSchema.names())
        self.assertTrue("first_weekday" in IDateAndTimeSchema.names())

    def test_first_weekday(self):
        # Make sure the first weekday was set when the profile was run.
        first_weekday = self.portal.portal_registry["plone.first_weekday"]
        self.assertEqual(first_weekday, 6)

        # Change the site language. Re-running the import step should not
        # change the setting.
        portal = self.portal
        old_language = portal.language
        portal.language = "de"
        from Products.CMFPlone.setuphandlers import first_weekday_setup

        first_weekday_setup(portal)
        first_weekday = self.portal.portal_registry["plone.first_weekday"]
        self.assertEqual(first_weekday, 6)

        # But if we remove the setting, re-running the step should set it based
        # on the language.
        self.portal.portal_registry["plone.first_weekday"] = None
        first_weekday_setup(portal)
        first_weekday = self.portal.portal_registry["plone.first_weekday"]
        self.assertEqual(first_weekday, 0)

        # Restore the site language.
        portal.language = old_language
