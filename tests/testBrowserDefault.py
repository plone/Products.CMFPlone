#
# Test the browserDefault script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy


class TestDefaultPage(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.ob = dummy.DefaultPage()
        sp = self.portal.portal_properties.site_properties
        self.default = sp.getProperty('default_page', [])

    def getDefault(self):
        return self.portal.plone_utils.browserDefault(self.ob)

    def testDefaultPageSetting(self):
        self.assertEquals(self.default, ('index_html', 'index.html',
                                         'index.htm', 'FrontPage'))

    def testDefaultPageStringExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default('test', 1)
        self.assertEquals(self.getDefault(), (self.ob, ['test']))

    def testDefaultPageStringNotExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default('test', 0)
        self.assertEquals(self.getDefault(), (self.ob, ['index_html']))

    def testDefaultPageSequenceExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default(['test'], 1)
        self.assertEquals(self.getDefault(), (self.ob, ['test']))

    def testDefaultPageSequenceNotExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default(['test'], 0)
        self.assertEquals(self.getDefault(), (self.ob, ['index_html']))
        self.ob.keys = ['index.html']
        self.assertEquals(self.getDefault(), (self.ob, ['index.html']))
        self.ob.keys = ['index.htm']
        self.assertEquals(self.getDefault(), (self.ob, ['index.htm']))
        self.ob.keys = ['FrontPage']
        self.assertEquals(self.getDefault(), (self.ob, ['FrontPage']))

    def testBrowserDefaultLayout(self):
        # Test assumes ATContentTypes + BrowserDefaultMixin + atct_album_view
        self.folder.setLayout('atct_album_view')
        self.assertEquals(self.portal.plone_utils.browserDefault(self.folder), 
                            (self.folder, ['atct_album_view']))

    def testBrowserDefaultPage(self):
        # Test assumes ATContentTypes + BrowserDefaultMixin
        self.folder.invokeFactory('Document', 'd1', title='document 1')
        self.folder.setDefaultPage('d1')
        self.assertEquals(self.portal.plone_utils.browserDefault(self.folder),
                            (self.folder, ['d1']))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDefaultPage))
    return suite

if __name__ == '__main__':
    framework()
