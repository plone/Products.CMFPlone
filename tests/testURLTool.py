#
# Tests the workflow tool
#

from Products.CMFPlone.tests import PloneTestCase

portal_name = PloneTestCase.portal_name


class TestURLTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.url = self.portal.portal_url

    def test_isURLInPortal(self):
        url_tool = self.url
        self.failUnless(url_tool.isURLInPortal(
                                        'http://nohost/%s/foo' % portal_name))
        self.failUnless(url_tool.isURLInPortal(
                                        'http://nohost/%s' % portal_name))
        self.failIf(url_tool.isURLInPortal(
                                        'http://nohost2/%s/foo' % portal_name))
        self.failUnless(url_tool.isURLInPortal(
                                        'https://nohost/%s/bar' % portal_name))
        self.failIf(url_tool.isURLInPortal(
                                   'http://nohost:8080/%s/baz' % portal_name))
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
