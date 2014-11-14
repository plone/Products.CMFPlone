# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ISearchSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getAdapter
from zope.component import getUtility
import unittest2 as unittest


class SearchControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.search_settings = registry.forInterface(
            ISearchSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, ISearchSchema))

    def test_get_enable_livesearch(self):
        self.assertEqual(
            getAdapter(self.portal, ISearchSchema).enable_livesearch,
            True
        )
        self.search_settings.enable_livesearch = False
        self.assertEquals(
            getAdapter(self.portal, ISearchSchema).enable_livesearch,
            False
        )

    def test_set_enable_livesearch(self):
        self.assertEquals(
            self.search_settings.enable_livesearch,
            True
        )
        getAdapter(self.portal, ISearchSchema).enable_livesearch = False
        self.assertEquals(
            self.search_settings.enable_livesearch,
            False
        )

    def test_get_types_not_searched(self):
        self.assertTrue(
            'Folder' not in
            getAdapter(self.portal, ISearchSchema).types_not_searched
        )
        self.search_settings.types_not_searched = ('Folder',)
        self.assertTrue(
            'Folder' in
            getAdapter(self.portal, ISearchSchema).types_not_searched
        )

    def test_set_types_not_searched(self):
        self.assertTrue(
            'Folder' not in self.search_settings.types_not_searched
        )
        getAdapter(self.portal, ISearchSchema).types_not_searched = ('Folder',)
        self.assertTrue(
            'Folder' in self.search_settings.types_not_searched
        )
