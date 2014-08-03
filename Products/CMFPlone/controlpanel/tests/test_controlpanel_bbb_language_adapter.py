# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ILanguageSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING

from plone.app.testing import TEST_USER_ID, setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import getAdapter

import unittest2 as unittest


class LanguageControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.navigation_settings = registry.forInterface(
            ILanguageSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, ILanguageSchema))

    def test_get_default_language(self):
        self.assertEqual(
            getAdapter(self.portal, ILanguageSchema).default_language,
            'en'
        )
        self.navigation_settings.default_language = 'de'
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).default_language,
            'de'
        )

    def test_set_default_language(self):
        self.assertEquals(
            self.navigation_settings.default_language,
            'en'
        )
        getAdapter(self.portal, ILanguageSchema).default_language = 'de'
        self.assertEquals(
            self.navigation_settings.default_language,
            'de'
        )
