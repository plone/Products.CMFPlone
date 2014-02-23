# -*- coding: utf-8 -*-
import unittest2 as unittest

from Products.CMFPlone.interfaces import ISiteSchema

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, setRoles

from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING


class SiteRegistryIntegrationTest(unittest.TestCase):
    """Test that the site settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_site_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="site-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_plone_app_registry_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue(
            'plone.app.registry' in
            [a.getAction(self)['id'] for a in self.controlpanel.listActions()]
        )

    def test_site_title_setting(self):
        self.assertTrue('site_title' in ISiteSchema.names())

    def test_exposeDCMetaTags_setting(self):
        self.assertTrue('exposeDCMetaTags' in ISiteSchema.names())

    def test_webstats_js_setting(self):
        self.assertTrue('webstats_js' in ISiteSchema.names())

    def test_enable_sitemap_setting(self):
        self.assertTrue('enable_sitemap' in ISiteSchema.names())
