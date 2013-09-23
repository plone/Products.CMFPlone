from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing.bbb import PloneTestCase
from urllib import urlencode
from urlparse import urlparse
import base64


class TestCookieAuth(PloneTestCase):

    def afterSetUp(self):
        self.portal_url = self.portal.absolute_url()
        self.portal_path = '/%s' % self.portal.absolute_url(1)
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.auth_info = '%s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD)
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
        form = {'__ac_name': TEST_USER_NAME, '__ac_password': TEST_USER_PASSWORD}

        response = self.publish(self.portal_path + '/logged_in',
                                env={'QUERY_STRING': urlencode(form)})

        self.assertEqual(response.getStatus(), 200)

        cookie = response.getCookie('__ac')
        self.assertEqual(cookie.get('path'), '/')
        self.assertEqual(cookie.get('expires'), None)
