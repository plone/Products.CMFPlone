# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getAdapter
from zope.component import getUtility
import unittest


class SiteControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISiteSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, ISiteSchema))

    def test_get_site_title(self):
        self.settings.site_title = u'Great Site'
        self.assertEquals(
            getAdapter(self.portal, ISiteSchema).site_title,
            u'Great Site'
        )

    def test_set_site_title(self):
        getAdapter(self.portal, ISiteSchema).site_title = u'Good Site'
        self.assertEquals(
            self.settings.site_title,
            u'Good Site'
        )

    def test_set_site_title_string(self):
        getAdapter(self.portal, ISiteSchema).site_title = 'Good Site'
        self.assertEquals(
            self.settings.site_title,
            u'Good Site'
        )

    def test_get_webstats_js(self):
        self.settings.webstats_js = u'Script Tag'
        self.assertEquals(
            getAdapter(self.portal, ISiteSchema).webstats_js,
            u'Script Tag'
        )

    def test_set_webstats_js(self):
        getAdapter(self.portal, ISiteSchema).webstats_js = u'Script Tag'
        self.assertEquals(
            self.settings.webstats_js,
            u'Script Tag'
        )

    def test_set_webstats_js_string(self):
        getAdapter(self.portal, ISiteSchema).webstats_js = 'Script Tag'
        self.assertEquals(
            self.settings.webstats_js,
            u'Script Tag'
        )
