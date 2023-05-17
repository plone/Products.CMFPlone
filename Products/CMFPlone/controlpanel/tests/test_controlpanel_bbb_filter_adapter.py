from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IFilterSchema
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getAdapter
from zope.component import getUtility

import unittest


class FilterControlPanelAdapterTest(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IFilterSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, IFilterSchema))

    def test_get_nasty_tags(self):
        self.settings.nasty_tags = ["foo", "bar"]
        self.assertEqual(
            getAdapter(self.portal, IFilterSchema).nasty_tags, ["foo", "bar"]
        )

    def test_set_nasty_tags(self):
        getAdapter(self.portal, IFilterSchema).nasty_tags = ["foo", "bar"]
        self.assertEqual(self.settings.nasty_tags, ["foo", "bar"])

    def test_get_valid_tags(self):
        self.settings.valid_tags = ["foo", "bar"]
        self.assertEqual(
            getAdapter(self.portal, IFilterSchema).valid_tags, ["foo", "bar"]
        )

    def test_set_valid_tags(self):
        getAdapter(self.portal, IFilterSchema).valid_tags = ["foo", "bar"]
        self.assertEqual(self.settings.valid_tags, ["foo", "bar"])

    def test_get_custom_attributes(self):
        self.settings.custom_attributes = ["foo", "bar"]
        self.assertEqual(
            getAdapter(self.portal, IFilterSchema).custom_attributes, ["foo", "bar"]
        )

    def test_set_custom_attributes(self):
        getAdapter(self.portal, IFilterSchema).custom_attributes = ["foo", "bar"]
        self.assertEqual(self.settings.custom_attributes, ["foo", "bar"])
