from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.i18n.interfaces import ILanguageSchema
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser

from zope.component import getMultiAdapter
from zope.component import getUtility

from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

import unittest
import webtest


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
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )

    def _inject_available_languages_field(self, value):
        """The in-and-out widget does not work without javascript, therefore
           we have to inject some values in order to make saving the form work.
        """
        form = self.browser.getForm(id='LanguageControlPanel')
        name = 'form.widgets.available_languages:list'
        field = webtest.forms.Hidden(form._form, 'input', name, 0, value=value)
        form._form.field_order.append((name, field))
        self.browser.getControl('Save').click()

    def test_language_control_panel_link(self):
        self.browser.open(
            "%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('Language').click()
        self.assertTrue("Language Settings" in self.browser.contents)

    def test_language_control_panel_backlink(self):
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertTrue("General" in self.browser.contents)

    def test_language_control_panel_sidebar(self):
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertTrue(
            self.browser.url.endswith('/plone/@@overview-controlpanel')
        )

    def test_language_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="language-controlpanel")
        self.assertTrue(view())

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
        self._inject_available_languages_field('en')
        self._inject_available_languages_field('de')
        self.browser.getControl(name='form.buttons.save').click()

        self.assertEqual(settings.default_language, 'de')

    # def test_available_languages(self):
    #     registry = getUtility(IRegistry)
    #     settings = registry.forInterface(ILanguageSchema, prefix='plone')
    #     self.browser.open(
    #         "%s/@@language-controlpanel" % self.portal_url)
    #     self.assertEqual(settings.available_languages, ['en'])
    #     self.assertEqual(
    #         self.browser.getControl(
    #             name='form.widgets.available_languages.to'
    #         ).options,
    #         ['en']
    #     )
    #     control = self.browser.getForm(index=1)
    #     self.in_out_select(
    #         control, 'form.widgets.available_languages:list', 'Deutsch')
    #     self.browser.getControl('Save').click()
    #     self.assertEqual(settings.available_languages, ['en', 'de'])

    def test_use_combined_language_codes(self):
        """This checks swithing combined languages codes support off/on."""
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.use_combined_language_codes, True)
        self.assertEqual(
            self.browser.getControl(
                'Show country-specific language variants'
            ).selected,
            True
        )
        self.browser.getControl(
            'Show country-specific language variants'
        ).selected = False

        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.use_combined_language_codes, False)

    def test_display_flags(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.display_flags, False)
        self.assertEqual(
            self.browser.getControl(
                'Show language flags'
            ).selected,
            False
        )
        self.browser.getControl(
            'Show language flags'
        ).selected = True

        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.display_flags, True)

    def test_use_content_negotiation(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.use_content_negotiation, False)
        self.assertEqual(
            self.browser.getControl(
                'Use the language of the content item'
            ).selected,
            False
        )
        self.browser.getControl(
            'Use the language of the content item'
        ).selected = True

        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.use_content_negotiation, True)

    def test_use_path_negotiation(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.use_path_negotiation, False)
        self.assertEqual(
            self.browser.getControl(
                'Use language codes in URL path for manual override'
            ).selected,
            False
        )
        self.browser.getControl(
            'Use language codes in URL path for manual override'
        ).selected = True

        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.use_path_negotiation, True)

    def test_use_cookie_negotiation(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.use_cookie_negotiation, False)
        self.assertEqual(
            self.browser.getControl(
                'Use cookie for manual override'
            ).selected,
            False
        )
        self.browser.getControl(
            'Use cookie for manual override'
        ).selected = True

        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.use_cookie_negotiation, True)

    def test_authenticated_users_only(self):
        control_label = "Authenticated users only"
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.authenticated_users_only, False)
        self.assertEqual(
            self.browser.getControl(control_label).selected,
            False
        )
        self.browser.getControl(control_label).selected = True

        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.authenticated_users_only, True)

    def test_set_cookie_always(self):
        control_label = "Set the language cookie always"
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.set_cookie_always, False)
        self.assertEqual(
            self.browser.getControl(control_label).selected,
            False
        )
        self.browser.getControl(control_label).selected = True
        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.set_cookie_always, True)

    def test_use_subdomain_negotiation(self):
        control_label = "Use subdomain"
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.use_subdomain_negotiation, False)
        self.assertEqual(
            self.browser.getControl(control_label).selected,
            False
        )
        self.browser.getControl(control_label).selected = True
        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.use_subdomain_negotiation, True)

    def test_use_cctld_negotiation(self):
        control_label = "Use top-level domain"
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.use_cctld_negotiation, False)
        self.assertEqual(
            self.browser.getControl(control_label).selected,
            False
        )
        self.browser.getControl(control_label).selected = True
        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.use_cctld_negotiation, True)

    def test_use_request_negotiation(self):
        control_label = "Use browser language request negotiation"
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix='plone')
        self.browser.open(
            "%s/@@language-controlpanel" % self.portal_url)
        self.assertEqual(settings.use_request_negotiation, False)
        self.assertEqual(
            self.browser.getControl(control_label).selected,
            False
        )
        self.browser.getControl(control_label).selected = True
        self._inject_available_languages_field('en')
        self.browser.getControl('Save').click()

        self.assertEqual(settings.use_request_negotiation, True)
