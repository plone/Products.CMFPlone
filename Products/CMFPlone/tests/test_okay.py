from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class OkayTest(unittest.TestCase):
    """Test the OK simple status view."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']

    def test_okay_browser(self):
        browser = Browser(self.app)
        app_url = self.app.absolute_url()
        portal_url = self.portal.absolute_url()
        # Try a couple of urls that should return the same.
        urls = (
            app_url + '/@@ok',
            app_url + '/ok?hello=1',
            portal_url + '/@@ok',
            portal_url + '/ok?hello=1',
        )
        for url in urls:
            browser.open(url)
            self.assertEqual(browser.contents, 'OK')
            get_header = browser.headers.get
            self.assertEqual(
                get_header('Expires'), 'Sat, 1 Jan 2000 00:00:00 GMT')
            self.assertEqual(
                get_header('Cache-Control'),
                'max-age=0, must-revalidate, private')
            # Getting it with a browser gives some more headings than accessing
            # the view directly.
            self.assertEqual(get_header('content-length'), '2')
            # content-type has a charset, but we don't really care about that.
            self.assertTrue(
                get_header('content-type').startswith('text/plain'))

    def test_okay_view(self):
        for page in (self.app, self.portal):
            view = page.restrictedTraverse('@@ok')
            self.assertEqual(view(), 'OK')
            get_header = view.request.response.getHeader
            self.assertEqual(
                get_header('Expires'), 'Sat, 1 Jan 2000 00:00:00 GMT')
            self.assertEqual(
                get_header('Cache-Control'),
                'max-age=0, must-revalidate, private')
