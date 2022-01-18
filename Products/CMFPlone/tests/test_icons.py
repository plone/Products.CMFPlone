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



class IconTraverserTest(unittest.TestCase):
    """Test the icon traverser or PloneBundlesTraverser."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_default_icon(self):
        self.portal.restrictedTraverse("++plone++icons/plone.svg")

    def test_bootstrap_icon(self):
        self.portal.restrictedTraverse("++plone++bootstrap-icons/clock.svg")

    def test_bootstrap_icon_with_path_info(self):
        """Get bootstrap icon while request has a PATH_INFO.

        When the request has PATH_INFO, which it normally has,
        the code originally ignored the remaining name (clock.svg)
        and tried to traverse based on this PATH_INFO.
        This works fine when the url of the request is for an icon.
        But when the url is for a normal page which tries to load an icon
        in the template, it fails.

        I don't know why most of the time it goes right.
        But I have occasionally seen failures.
        And it happens at least in plone.i18n tests.
        https://github.com/plone/plone.i18n/pull/41
        """
        self.request.environ["PATH_INFO"] = "plone"
        self.portal.restrictedTraverse("++plone++bootstrap-icons/clock.svg")
