#
# CookieCrumbler tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

import base64


class TestCookieCrumbler(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.portal_url = self.portal.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.cookie = base64.encodestring('%s:secret' % PloneTestCase.default_user)
        self.folder.manage_permission('View', ['Manager'], acquire=0)

    def testAutoLoginPage(self):
        # Should send us to the login_form
        response = self.publish(self.folder_path)
        self.assertEqual(response.getStatus(), 302)

        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.portal_url + '/login_form'))

    def testInsufficientPrivileges(self):
        # Should send us to insufficient_privileges
        response = self.publish(self.folder_path, extra={'__ac': self.cookie})
        self.assertEqual(response.getStatus(), 302)

        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.portal_url + '/insufficient_privileges'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCookieCrumbler))
    return suite

if __name__ == '__main__':
    framework()
