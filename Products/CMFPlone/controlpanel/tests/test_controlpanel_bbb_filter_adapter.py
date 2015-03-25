# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getAdapter
from zope.component import getUtility
import unittest


class FilterControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IFilterSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, IFilterSchema))

    def test_get_nasty_tags(self):
        self.settings.nasty_tags = [u'foo', u'bar']
        self.assertEquals(
            getAdapter(self.portal, IFilterSchema).nasty_tags,
            [u'foo', u'bar']
        )

    def test_set_nasty_tags(self):
        getAdapter(self.portal, IFilterSchema).nasty_tags = [u'foo', u'bar']
        self.assertEquals(
            self.settings.nasty_tags,
            [u'foo', u'bar']
        )

    def test_get_stripped_tags(self):
        self.settings.stripped_tags = [u'foo', u'bar']
        self.assertEquals(
            getAdapter(self.portal, IFilterSchema).stripped_tags,
            [u'foo', u'bar']
        )

    def test_set_stripped_tags(self):
        getAdapter(self.portal, IFilterSchema).stripped_tags = [u'foo', u'bar']
        self.assertEquals(
            self.settings.stripped_tags,
            [u'foo', u'bar']
        )

    def test_get_custom_tags(self):
        self.settings.custom_tags = [u'foo', u'bar']
        self.assertEquals(
            getAdapter(self.portal, IFilterSchema).custom_tags,
            [u'foo', u'bar']
        )

    def test_set_custom_tags(self):
        getAdapter(self.portal, IFilterSchema).custom_tags = [u'foo', u'bar']
        self.assertEquals(
            self.settings.custom_tags,
            [u'foo', u'bar']
        )

    def test_get_stripped_attributes(self):
        self.settings.stripped_attributes = [u'foo', u'bar']
        self.assertEquals(
            getAdapter(self.portal, IFilterSchema).stripped_attributes,
            [u'foo', u'bar']
        )

    def test_set_stripped_attributes(self):
        getAdapter(self.portal, IFilterSchema).stripped_attributes = [
            u'foo', u'bar'
        ]
        self.assertEquals(
            self.settings.stripped_attributes,
            [u'foo', u'bar']
        )

    def test_get_style_whitelist(self):
        self.settings.style_whitelist = [u'foo', u'bar']
        self.assertEquals(
            getAdapter(self.portal, IFilterSchema).style_whitelist,
            [u'foo', u'bar']
        )

    def test_set_style_whitelist(self):
        getAdapter(self.portal, IFilterSchema).style_whitelist = [
            u'foo', u'bar'
        ]
        self.assertEquals(
            self.settings.style_whitelist,
            [u'foo', u'bar']
        )

    def test_get_class_blacklist(self):
        self.settings.class_blacklist = [u'foo', u'bar']
        self.assertEquals(
            getAdapter(self.portal, IFilterSchema).class_blacklist,
            [u'foo', u'bar']
        )

    def test_set_class_blacklist(self):
        getAdapter(self.portal, IFilterSchema).class_blacklist = [
            u'foo', u'bar'
        ]
        self.assertEquals(
            self.settings.class_blacklist,
            [u'foo', u'bar']
        )
