# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser

from zope.component import getMultiAdapter
from zope.component import getUtility

from Products.CMFPlone.interfaces import ILanguageSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

import unittest2 as unittest


class LanguageControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the language control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_language_control_panel_link(self):
        self.browser.open(
            "%s/plone_control_panel" % self.portal_url)
        self.browser.getLink('Language').click()
        self.assertTrue("Language Settings" in self.browser.contents)

    def test_language_control_panel_backlink(self):
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertTrue("Plone Configuration" in self.browser.contents)

    def test_language_control_panel_sidebar(self):
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/@@overview-controlpanel')

    def test_language_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="language-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_use_combined_language_codes(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.use_combined_language_codes, False)
        self.assertEqual(
            self.browser.getControl(
                'Show country-specific language variants'
            ).selected,
            False
        )
        self.browser.getControl(
            'Show country-specific language variants'
        ).selected = True
        self.browser.getControl('Save').click()

        self.assertEqual(settings.use_combined_language_codes, True)

    def test_default_language(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.default_language, 'en')
        self.assertEqual(
            self.browser.getControl(
                'Site language'
            ).value,
            ['en']
        )
        self.browser.getControl(
            'Site language'
        ).value = ['de']
        self.browser.getControl('Save').click()

        self.assertEqual(settings.default_language, 'de')
