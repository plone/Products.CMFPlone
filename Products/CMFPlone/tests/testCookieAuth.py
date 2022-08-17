from plone.app.testing import logout
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

import unittest

try:
    from base64 import encodebytes
except ImportError:
    from base64 import encodestring as encodebytes


class TestCookieAuth(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['test-folder']
        self.browser = Browser(self.layer['app'])
        self.auth_info = f'{TEST_USER_NAME}:{TEST_USER_PASSWORD}'
        self.cookie = encodebytes(self.auth_info.encode('utf8'))[:-1]
        self.folder.manage_permission('View', ['Manager'], acquire=0)
        logout()

    def testAutoLoginPage(self):
        # Should send us to login_form
        self.browser.open(self.folder.absolute_url())
        self.assertIn('200', self.browser.headers['status'])
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/login?came_from=/plone/test-folder'  # noqa: E501
        )

    def testInsufficientPrivileges(self):
        # Should send us to login_form
        self.browser.open(self.portal.absolute_url())
        self.browser.cookies['__ac'] = self.cookie
        self.browser.open(self.folder.absolute_url())
        self.assertIn('200', self.browser.headers['status'])
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/login?came_from=/plone/test-folder'  # noqa: E501
        )

    def testSetSessionCookie(self):
        # The __ac cookie should be set for the session only
        self.browser.open('http://nohost/plone/login')
        self.browser.getControl(name='__ac_name').value = TEST_USER_NAME
        self.browser.getControl(
            name='__ac_password'
        ).value = TEST_USER_PASSWORD
        self.browser.getControl('Log in').click()
        self.assertIn('200', self.browser.headers['status'])
        self.assertIn('__ac', self.browser.cookies)
        self.assertEqual(
            self.browser.cookies.getinfo('__ac')['path'],
            '/',
        )
        self.assertIsNone(self.browser.cookies.getinfo('__ac')['expires'])
