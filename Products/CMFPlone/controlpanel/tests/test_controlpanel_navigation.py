# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest2 as unittest


class NavigationRegistryIntegrationTest(unittest.TestCase):
    """Test that the navigation settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def test_generate_tabs(self):
        self.assertTrue('generate_tabs' in INavigationSchema.names())

    def test_nonfolderish_tabs(self):
        self.assertTrue('nonfolderish_tabs' in INavigationSchema.names())

    def test_displayed_types(self):
        self.assertTrue('displayed_types' in INavigationSchema.names())

    def test_filter_on_workflow(self):
        self.assertTrue('filter_on_workflow' in INavigationSchema.names())

    def test_workflow_states_to_show(self):
        self.assertTrue('workflow_states_to_show' in INavigationSchema.names())

    def test_show_excluded_items(self):
        self.assertTrue('show_excluded_items' in INavigationSchema.names())
