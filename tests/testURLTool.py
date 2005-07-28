#
# Tests the workflow tool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase



class TestURLTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.url = self.portal.portal_url

    def test_isURLInPortal(self):
        url_tool = self.url
        self.failUnless(url_tool.isURLInPortal(
                                        'http://nohost/portal/foo'))
        self.failUnless(url_tool.isURLInPortal(
                                        'http://nohost/portal'))
        self.failIf(url_tool.isURLInPortal(
                                        'http://nohost2/portal/foo'))
        self.failUnless(url_tool.isURLInPortal(
                                        'https://nohost/portal/bar'))
        self.failIf(url_tool.isURLInPortal(
                                   'http://nohost:8080/portal/baz'))
        self.failIf(url_tool.isURLInPortal(
                                   'http://nohost/'))
        # Relative urls always succeed
        self.failUnless(url_tool.isURLInPortal(
                                   '/images'))
        self.failUnless(url_tool.isURLInPortal(
                                   'images/img1.jpg'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestURLTool))
    return suite

if __name__ == '__main__':
    framework()
