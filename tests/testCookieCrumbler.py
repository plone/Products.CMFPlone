#
# CookieCrumbler tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

import base64
from urlparse import urlparse

default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password


class TestCookieCrumbler(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.portal_url = self.portal.absolute_url()
        self.portal_path = '/%s' % self.portal.absolute_url(1)
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.auth_info = '%s:%s' % (default_user, default_password)
        self.cookie = base64.encodestring(self.auth_info)[:-1]
        self.folder.manage_permission('View', ['Manager'], acquire=0)

    def testAutoLoginPage(self):
        # Should send us to the login_form
        response = self.publish(self.folder_path)
        self.assertEqual(response.getStatus(), 302)

        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.portal_url))
        self.failUnless(urlparse(location)[2].endswith('/login_form'))

    def testInsufficientPrivileges(self):
        # Should send us to insufficient_privileges
        response = self.publish(self.folder_path, extra={'__ac': self.cookie})
        self.assertEqual(response.getStatus(), 302)

        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.portal_url))
        urlpath=urlparse(location)[2]
        self.failUnless(urlpath.endswith('/insufficient_privileges') or
            urlpath.endswith('/login_form'))

    def testSetSessionCookie(self):
        # The __ac cookie should be set for the session only
        form = {'__ac_name': default_user, '__ac_password': default_password}

        response = self.publish(self.portal_path + '/logged_in', extra=form)
        self.assertEqual(response.getStatus(), 200)

        cookie = response.getCookie('__ac')
        self.assertEqual(cookie.get('path'), '/')
        self.assertEqual(cookie.get('value'), self.cookie)
        self.assertEqual(cookie.get('expires'), None)

    def testSetPersistentCookie(self):
        # The __ac cookie should be set for 7 days
        self.portal.portal_properties.site_properties.auth_cookie_length = 7
        form = {'__ac_name': default_user, '__ac_password': default_password}

        response = self.publish(self.portal_path + '/logged_in', extra=form)
        self.assertEqual(response.getStatus(), 200)

        cookie = response.getCookie('__ac')
        self.assertEqual(cookie.get('path'), '/')
        self.assertEqual(cookie.get('value'), self.cookie)
        self.failIfEqual(cookie.get('expires'), None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCookieCrumbler))
    return suite

if __name__ == '__main__':
    framework()
