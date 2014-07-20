# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest2 as unittest


class SiteRegistryIntegrationTest(unittest.TestCase):
    """Test that the site settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def test_site_title_setting(self):
        self.assertTrue('site_title' in ISiteSchema.names())

    def test_exposeDCMetaTags_setting(self):
        self.assertTrue('exposeDCMetaTags' in ISiteSchema.names())

    def test_webstats_js_setting(self):
        self.assertTrue('webstats_js' in ISiteSchema.names())

    def test_enable_sitemap_setting(self):
        self.assertTrue('enable_sitemap' in ISiteSchema.names())
