# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
import unittest2 as unittest


class SiteRegistryIntegrationTest(unittest.TestCase):
    """Test that the site settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ISiteSchema, prefix="plone")

    def test_search_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="search-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_search_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('SearchSettings' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()
        ])

    def test_site_title_setting(self):
        self.assertTrue(hasattr(self.settings, 'site_title'))

    def test_site_logo_setting(self):
        self.assertTrue(hasattr(self.settings, 'site_logo'))

    def test_exposeDCMetaTags_setting(self):
        self.assertTrue(hasattr(self.settings, 'exposeDCMetaTags'))

    def test_webstats_js_setting(self):
        self.assertTrue(hasattr(self.settings, 'webstats_js'))

    def test_enable_sitemap_setting(self):
        self.assertTrue(hasattr(self.settings, 'enable_sitemap'))
