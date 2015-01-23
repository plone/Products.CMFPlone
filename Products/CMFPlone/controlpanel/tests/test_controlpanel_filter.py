# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
import unittest2 as unittest


class FilterRegistryIntegrationTest(unittest.TestCase):
    """Test that the filter settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):  # NOQA
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")

    def test_filter_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="filter-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_filter_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('FilterSettings' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()
        ])

    def test_disable_filtering_setting(self):
        self.assertTrue(hasattr(self.settings, 'disable_filtering'))

    def test_nasty_tags_setting(self):
        self.assertTrue(hasattr(self.settings, 'nasty_tags'))

    def test_stripped_tags_setting(self):
        self.assertTrue(hasattr(self.settings, 'stripped_tags'))

    def test_custom_tags_setting(self):
        self.assertTrue(hasattr(self.settings, 'custom_tags'))

    def test_stripped_attributes_setting(self):
        self.assertTrue(hasattr(self.settings, 'stripped_attributes'))

    # def test_stripped_combinations_setting(self):
    #     self.assertTrue(hasattr(self.settings, 'stripped_combinations'))

    def test_style_whitelist_setting(self):
        self.assertTrue(hasattr(self.settings, 'style_whitelist'))

    def test_class_blacklist_setting(self):
        self.assertTrue(hasattr(self.settings, 'class_blacklist'))
