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
        self.settings = registry.forInterface(
            ILanguageSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, ILanguageSchema))

    def test_get_default_language(self):
        self.assertEqual(
            getAdapter(self.portal, ILanguageSchema).default_language,
            'en'
        )
        self.settings.default_language = 'de'
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).default_language,
            'de'
        )

    def test_set_default_language(self):
        self.assertEquals(
            self.settings.default_language,
            'en'
        )
        getAdapter(self.portal, ILanguageSchema).default_language = 'de'
        self.assertEquals(
            self.settings.default_language,
            'de'
        )

    def test_get_available_languages(self):
        self.assertEqual(
            getAdapter(self.portal, ILanguageSchema).available_languages,
            ['en']
        )
        self.settings.available_languages = ['en', 'de']
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).available_languages,
            ['en', 'de']
        )

    def test_set_available_languages(self):
        self.assertEquals(
            self.settings.available_languages,
            ['en']
        )
        getAdapter(self.portal, ILanguageSchema).available_languages = ['de', 'en']
        self.assertEquals(
            self.settings.available_languages,
            ['de', 'en']
        )

    def test_get_use_combined_language_codes(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).use_combined_language_codes,
            True
        )
        self.settings.use_combined_language_codes = False
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).use_combined_language_codes,
            False
        )

    def test_set_use_combined_language_codes(self):
        self.assertEquals(
            self.settings.use_combined_language_codes,
            True
        )
        getAdapter(
              self.portal, ILanguageSchema).use_combined_language_codes = False
        self.assertEquals(
            self.settings.use_combined_language_codes,
            False
        )

    def test_get_display_flags(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).display_flags,
            False
        )
        self.settings.display_flags = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).display_flags,
            True
        )

    def test_set_display_flags(self):
        self.assertEquals(
            self.settings.display_flags,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).display_flags = True
        self.assertEquals(
            self.settings.display_flags,
            True
        )

    def test_get_use_content_negotiation(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).use_content_negotiation,
            False
        )
        self.settings.use_content_negotiation = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).use_content_negotiation,
            True
        )

    def test_set_use_content_negotiation(self):
        self.assertEquals(
            self.settings.use_content_negotiation,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).use_content_negotiation = True
        self.assertEquals(
            self.settings.use_content_negotiation,
            True
        )

    def test_get_use_path_negotiation(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).use_path_negotiation,
            False
        )
        self.settings.use_path_negotiation = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).use_path_negotiation,
            True
        )

    def test_set_use_path_negotiation(self):
        self.assertEquals(
            self.settings.use_path_negotiation,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).use_path_negotiation = True
        self.assertEquals(
            self.settings.use_path_negotiation,
            True
        )

    def test_get_use_cookie_negotiation(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).use_cookie_negotiation,
            False
        )
        self.settings.use_cookie_negotiation = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).use_cookie_negotiation,
            True
        )

    def test_set_use_cookie_negotiation(self):
        self.assertEquals(
            self.settings.use_cookie_negotiation,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).use_cookie_negotiation = True
        self.assertEquals(
            self.settings.use_cookie_negotiation,
            True
        )

    def test_get_authenticated_users_only(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).authenticated_users_only,
            False
        )
        self.settings.authenticated_users_only = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).authenticated_users_only,
            True
        )

    def test_set_authenticated_users_only(self):
        self.assertEquals(
            self.settings.authenticated_users_only,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).authenticated_users_only = True
        self.assertEquals(
            self.settings.authenticated_users_only,
            True
        )

    def test_get_set_cookie_always(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).set_cookie_always,
            False
        )
        self.settings.set_cookie_always = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).set_cookie_always,
            True
        )

    def test_set_set_cookie_always(self):
        self.assertEquals(
            self.settings.set_cookie_always,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).set_cookie_always = True
        self.assertEquals(
            self.settings.set_cookie_always,
            True
        )

    def test_get_use_subdomain_negotiation(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).use_subdomain_negotiation,
            False
        )
        self.settings.use_subdomain_negotiation = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).use_subdomain_negotiation,
            True
        )

    def test_set_use_subdomain_negotiation(self):
        self.assertEquals(
            self.settings.use_subdomain_negotiation,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).use_subdomain_negotiation = True
        self.assertEquals(
            self.settings.use_subdomain_negotiation,
            True
        )

    def test_get_use_cctld_negotiation(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).use_cctld_negotiation,
            False
        )
        self.settings.use_cctld_negotiation = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).use_cctld_negotiation,
            True
        )

    def test_set_use_cctld_negotiation(self):
        self.assertEquals(
            self.settings.use_cctld_negotiation,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).use_cctld_negotiation = True
        self.assertEquals(
            self.settings.use_cctld_negotiation,
            True
        )

    def test_get_use_request_negotiation(self):
        self.assertEqual(
            getAdapter(
                self.portal, ILanguageSchema).use_request_negotiation,
            False
        )
        self.settings.use_request_negotiation = True
        self.assertEquals(
            getAdapter(self.portal, ILanguageSchema).use_request_negotiation,
            True
        )

    def test_set_use_request_negotiation(self):
        self.assertEquals(
            self.settings.use_request_negotiation,
            False
        )
        getAdapter(
            self.portal, ILanguageSchema).use_request_negotiation = True
        self.assertEquals(
            self.settings.use_request_negotiation,
            True
        )

