from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class IconsTest(unittest.TestCase):
    """Test the icon resolver view."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_icons_browser(self):
        browser = Browser(self.app)
        portal_url = self.portal.absolute_url()
        url = portal_url + '/@@iconresolver/bug'
        browser.open(url)
        self.assertIn(b'bi bi-bug', browser.contents)

    def test_icons_view(self):
        page = self.app
        view = page.restrictedTraverse('@@iconresolver')
        self.assertIn(b'bi bi-bug', view.tag('bug'))

    def test_icons_url(self):
        page = self.app
        view = page.restrictedTraverse('@@iconresolver')
        self.assertIn(
            '++plone++bootstrap-icons/bug.svg',
            view.url('bug')
        )

    def test_icons_tag(self):
        page = self.app
        view = page.restrictedTraverse('@@iconresolver')
        self.assertIn(b'bi bi-bug', view.tag('bug'))