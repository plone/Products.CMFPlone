from Products.CMFPlone.tests import PloneTestCase

import base64
from urlparse import urlparse
from urllib import urlencode

default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password


class TestCookieAuth(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.portal_url = self.portal.absolute_url()
        self.portal_path = '/%s' % self.portal.absolute_url(1)
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.auth_info = '%s:%s' % (default_user, default_password)
        self.cookie = base64.encodestring(self.auth_info)[:-1]
        self.folder.manage_permission('View', ['Manager'], acquire=0)

    def testAutoLoginPage(self):
        # Should send us to login_form
        response = self.publish(self.folder_path)
        self.assertEqual(response.getStatus(), 302)

        location = response.getHeader('Location')
        self.assertTrue(location.startswith(self.portal_url))
        self.assertTrue(urlparse(location)[2].endswith('/require_login'))

    def testInsufficientPrivileges(self):
        # Should send us to login_form
        response = self.publish(self.folder_path, env={'__ac': self.cookie})
        self.assertEqual(response.getStatus(), 302)

        location = response.getHeader('Location')
        self.assertTrue(location.startswith(self.portal_url))
        self.assertTrue(urlparse(location)[2].endswith('/require_login'))

    def testSetSessionCookie(self):
        # The __ac cookie should be set for the session only
        form = {'__ac_name': default_user, '__ac_password': default_password}

        response = self.publish(self.portal_path + '/logged_in',
                                env={'QUERY_STRING': urlencode(form)})

        self.assertEqual(response.getStatus(), 200)

        cookie = response.getCookie('__ac')
        self.assertEqual(cookie.get('path'), '/')
        self.assertEqual(cookie.get('expires'), None)
