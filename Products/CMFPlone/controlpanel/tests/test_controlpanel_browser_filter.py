from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.PortalTransforms.data import datastream
from zope.component import getMultiAdapter
from zope.component import getUtility
import unittest


class FilterControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the site control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )
        self.safe_html = getattr(
            getToolByName(self.portal, 'portal_transforms'),
            'safe_html',
            None)

    def test_filter_control_panel_link(self):
        self.browser.open(
            "%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('Site').click()

    def test_filter_control_panel_backlink(self):
        self.browser.open(
            "%s/@@filter-controlpanel" % self.portal_url)
        self.assertTrue("Security" in self.browser.contents)

    def test_filter_control_panel_sidebar(self):
        self.browser.open(
            "%s/@@filter-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertTrue(
            self.browser.url.endswith('/plone/@@overview-controlpanel')
        )

    def test_filter_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="filter-controlpanel")
        self.assertTrue(view())

    def test_disable_filtering(self):
        self.browser.open(
            "%s/@@filter-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.disable_filtering:list').value = "selected"
        self.browser.getControl('Save').click()

        # test that the transform is disabled
        self.assertEqual(
            self.settings.disable_filtering,
            1)

        # anything passes
        nasty_html = '<script></script>'
        ds = datastream('dummy_name')
        self.assertEqual(
            nasty_html,
            str(self.safe_html.convert(nasty_html, ds))
        )

    def test_nasty_tags(self):
        self.browser.open(
            "%s/@@filter-controlpanel" % self.portal_url)
        self.assertEqual(
            self.browser.getControl(name='form.widgets.nasty_tags').value,
            'style\nobject\nembed\napplet\nscript\nmeta')
        self.browser.getControl(
            name='form.widgets.nasty_tags').value = 'div\na'
        valid_tags = self.browser.getControl(
            name='form.widgets.valid_tags').value
        self.assertTrue(valid_tags.startswith('a\nabbr\nacronym\naddress'))
        valid_tags = valid_tags.replace('a\n', '')
        valid_tags = self.browser.getControl(
            name='form.widgets.valid_tags').value = valid_tags
        self.browser.getControl('Save').click()
        self.assertEqual(self.settings.nasty_tags, ['div', 'a'])
        self.assertNotIn('a', self.settings.valid_tags)

        # test that <a> is filtered
        self.assertFalse(self.settings.disable_filtering)
        good_html = '<p><a href="http://example.com">harmless link</a></p>'
        ds = datastream('dummy_name')
        self.assertEqual(
            self.safe_html.convert(good_html, ds).getData(),
            '<p></p>'
        )
