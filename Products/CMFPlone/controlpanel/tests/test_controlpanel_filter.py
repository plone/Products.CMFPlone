from plone.base.interfaces import IFilterSchema
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class FilterRegistryIntegrationTest(unittest.TestCase):
    """Test that the filter settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):  # NOQA
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IFilterSchema, prefix="plone")

    def test_filter_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="filter-controlpanel"
        )
        self.assertTrue(view())

    def test_filter_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue(
            "FilterSettings"
            in [a.getAction(self)["id"] for a in self.controlpanel.listActions()]
        )

    def test_disable_filtering_setting(self):
        self.assertTrue(hasattr(self.settings, "disable_filtering"))

    def test_nasty_tags_setting(self):
        self.assertTrue(hasattr(self.settings, "nasty_tags"))

    def test_valid_tags_setting(self):
        self.assertTrue(hasattr(self.settings, "valid_tags"))

    def test_custom_attributes_setting(self):
        self.assertTrue(hasattr(self.settings, "custom_attributes"))
