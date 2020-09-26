from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zope.testbrowser.browser import HostNotAllowed

import unittest


class TestPloneRootLoginURL(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )

    def test_normal_redirect(self):
        url = '/@@plone-root-login?came_from=%s' % self.portal.absolute_url()
        self.browser.open(self.app.absolute_url() + url)
        self.assertNotEqual(self.browser.url, None)
        self.assertEqual(self.browser.url,
                         self.portal.absolute_url())

    def test_attacker_redirect(self):
        attackers = (
            'http://attacker.com',
            '\\attacker.com',
        )
        for attacker in attackers:
            url = '@@plone-root-login?came_from=%s' % attacker
            with self.assertRaises(HostNotAllowed):
                self.browser.open(self.app.absolute_url() + url)
