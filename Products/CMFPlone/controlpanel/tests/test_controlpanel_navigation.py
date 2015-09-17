# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
import unittest2 as unittest


class NavigationRegistryIntegrationTest(unittest.TestCase):
    """Test that the navigation settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            INavigationSchema, prefix="plone")

    def test_navigation_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="navigation-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_navigation_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('NavigationSettings' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()
        ])

    def test_generate_tabs_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, 'generate_tabs'))

    def test_displayed_types_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, 'displayed_types'))

    def test_filter_on_workflow_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, 'filter_on_workflow'))

    def test_workflow_states_to_show_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, 'workflow_states_to_show'))

    def test_show_excluded_items_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, 'show_excluded_items'))
