from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.i18n.interfaces import ILanguageSchema
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class LanguageRegistryIntegrationTest(unittest.TestCase):
    """Test that the Language settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ILanguageSchema, prefix="plone")

    def test_language_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="language-controlpanel")
        self.assertTrue(view())

    def test_language_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('LanguageSettings' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()
        ])

    def test_default_language_exists(self):
        self.assertTrue(hasattr(self.settings, 'default_language'))

    def test_available_languages_exists(self):
        self.assertTrue(hasattr(self.settings, 'available_languages'))

    def test_use_combined_language_codes_exists(self):
        self.assertTrue(hasattr(self.settings, 'use_combined_language_codes'))

    def test_display_flags_exists(self):
        self.assertTrue(hasattr(self.settings, 'display_flags'))

    def test_use_content_negotiation_exists(self):
        self.assertTrue(hasattr(self.settings, 'use_content_negotiation'))

    def test_use_path_negotiation_exists(self):
        self.assertTrue(hasattr(self.settings, 'use_path_negotiation'))

    def test_use_cookie_negotiation_exists(self):
        self.assertTrue(hasattr(self.settings, 'use_cookie_negotiation'))

    def test_authenticated_users_only(self):
        self.assertTrue(hasattr(self.settings, 'authenticated_users_only'))

    def test_set_cookie_always(self):
        self.assertTrue(hasattr(self.settings, 'set_cookie_always'))

    def test_use_subdomain_negotiation(self):
        self.assertTrue(hasattr(self.settings, 'use_subdomain_negotiation'))

    def test_use_cctld_negotiation(self):
        self.assertTrue(hasattr(self.settings, 'use_cctld_negotiation'))

    def test_use_request_negotiation(self):
        self.assertTrue(hasattr(self.settings, 'use_request_negotiation'))
