# -*- coding: utf-8 -*-

from plone.app.layout.testing import FUNCTIONAL_TESTING
from plone.testing.z2 import Browser

import unittest


class ViewletTestCase(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_canonical_url_viewlet(self):
        portal_url = self.portal.absolute_url()
        canonical_link = '<link rel="canonical" href="%s"' % portal_url
        browser = Browser(self.layer['app'])
        # the page must contain the canonical URL link
        browser.open(portal_url)
        self.assertIn(canonical_link, browser.contents)
        # opening the same page using a different view must return the same
        # canonical URL
        browser.open(portal_url + '/view')
        self.assertIn(canonical_link, browser.contents)
