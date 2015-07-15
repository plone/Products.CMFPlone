# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.PortalTransforms.data import datastream
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from zope.component import getMultiAdapter
import unittest2 as unittest


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
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
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
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/@@overview-controlpanel')

    def test_filter_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="filter-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_disable_filtering(self):
        self.browser.open(
            "%s/@@filter-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.disable_filtering:list').value = "selected"
        self.browser.getControl('Save').click()

        # test that the transform is disabled
        self.assertEqual(
            self.safe_html._config['disable_transform'],
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
        self.browser.getControl(
            name='form.widgets.nasty_tags'
        ).value = 'div\r\na'
        self.browser.getControl('Save').click()

        # test that <a> is filtered
        self.assertFalse(self.safe_html._config['disable_transform'])
        good_html = '<a href="http://example.com">harmless link</a>'
        ds = datastream('dummy_name')
        self.assertEqual(
            str(self.safe_html.convert(good_html, ds)),
            ''
        )

    @unittest.skip('This functionality was broken with formlib already. Needs fix.')  # noqa
    def test_stripped_combinations(self):
        # test a combination that isn't normally filtered
        self.assertFalse(self.safe_html._config['disable_transform'])
        html = '<p class="wow">lala</p>'
        ds = datastream('dummy_name')
        self.assertEqual(
            str(self.safe_html.convert(html, ds)),
            html)

        # we can set stripped combinations
        self.browser.open(
            "%s/@@filter-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.stripped_combinations.buttons.add').click()
        self.browser.getControl(
            name='form.widgets.stripped_combinations.key.0'
        ).value = 'mytag1 p'
        self.browser.getControl(
            name='form.widgets.stripped_combinations.0'
        ).value = 'myattr1 class'
        self.browser.getControl('Save').click()

        # stripped combinations are stored on the transform
        self.assertIn(
            'mytag1 p',
            self.safe_html._config['stripped_combinations'])
        self.assertEqual(
            'myattr1 class',
            self.safe_html._config['stripped_combinations']['mytag1 p'])

        # test that combination is now filtered
        self.assertEqual(
            str(self.safe_html.convert(html, ds)),
            '<p>lala</p>')
