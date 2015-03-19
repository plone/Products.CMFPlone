# -*- coding: utf-8 -*-
# from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from zope.component import getMultiAdapter
import unittest2 as unittest


class FilterControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the site control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_filter_control_panel_link(self):
        self.browser.open(
            "%s/plone_control_panel" % self.portal_url)
        self.browser.getLink('Site').click()

    def test_filter_control_panel_backlink(self):
        self.browser.open(
            "%s/@@filter-controlpanel" % self.portal_url)
        self.assertTrue("Plone Configuration" in self.browser.contents)

    def test_filter_control_panel_sidebar(self):
        self.browser.open(
            "%s/@@filter-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/@@overview-controlpanel')

    def test_filter_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="filter-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())
