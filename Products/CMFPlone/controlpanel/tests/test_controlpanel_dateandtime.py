# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IDateAndTimeSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles

import unittest2 as unittest


class DateAndTimeRegistryIntegrationTest(unittest.TestCase):
    """Test date and time related settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portal_timezone_setting(self):
        self.assertTrue('portal_timezone' in IDateAndTimeSchema.names())

    def test_available_timezones_setting(self):
        self.assertTrue('available_timezones' in IDateAndTimeSchema.names())

    def test_first_weekday_setting(self):
        self.assertTrue('first_weekday' in IDateAndTimeSchema.names())
