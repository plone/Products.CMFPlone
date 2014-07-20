# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest2 as unittest


class SearchRegistryIntegrationTest(unittest.TestCase):
    """Test that the search settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def test_enable_livesearch_setting(self):
        self.assertTrue('enable_livesearch' in ISearchSchema.names())

    def test_types_not_searched(self):
        self.assertTrue('types_not_searched' in ISearchSchema.names())
