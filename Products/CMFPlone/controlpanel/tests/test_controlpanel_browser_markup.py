from Products.CMFPlone.interfaces import IMarkupSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from zope.component import getMultiAdapter
from zope.component import getUtility
import unittest


class MarkupControlPanelFunctionalTest(unittest.TestCase):
    """Make sure changes in the markup control panel are properly
    stored in plone.app.registry.
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

    def test_markup_control_panel_link(self):
        self.browser.open(
            "%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('Markup').click()

    def test_markup_control_panel_backlink(self):
        self.browser.open(
            "%s/@@markup-controlpanel" % self.portal_url)
        self.assertTrue("Content" in self.browser.contents)

    def test_markup_control_panel_sidebar(self):
        self.browser.open(
            "%s/@@markup-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertTrue(
            self.browser.url.endswith('/plone/@@overview-controlpanel')
        )

    def test_markup_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="markup-controlpanel")
        self.assertTrue(view())

    def test_default_type(self):
        self.browser.open(
            "%s/@@markup-controlpanel" % self.portal_url)
        self.browser.getControl('Default format').value = ['text/plain']
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMarkupSchema, prefix='plone')
        self.assertEqual(settings.default_type, 'text/plain')

    def test_allowed_types(self):
        self.browser.open(
            "%s/@@markup-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.allowed_types:list'
        ).value = ['text/html', 'text/x-web-textile']
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMarkupSchema, prefix='plone')
        self.assertEqual(settings.allowed_types,
                         ('text/html', 'text/x-web-textile'))

    def test_markdown_extensions(self):
        self.browser.open(
            "%s/@@markup-controlpanel" % self.portal_url)
        self.assertEqual(
            self.browser.getControl(
                name='form.widgets.markdown_extensions'
            ).value,
            'markdown.extensions.fenced_code\nmarkdown.extensions.nl2br')

        self.browser.getControl(
            name='form.widgets.markdown_extensions'
        ).value = '\n'.join([
            'markdown.extensions.fenced_code',
            'markdown.extensions.nl2br',
            'markdown.extensions.extra',
        ])
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMarkupSchema, prefix='plone')
        self.assertEqual(
            settings.markdown_extensions,
            [
                'markdown.extensions.fenced_code',
                'markdown.extensions.nl2br',
                'markdown.extensions.extra',
            ]
        )
