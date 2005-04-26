#
# Test methods used to make browser-default-mixin enabled display menu work
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy


class TestTemplateMixinScripts(PloneTestCase.PloneTestCase):
    '''Tests the browser default and folder-default page scripts'''

    def testNoIndexHtml(self):
        # A folder shouldn't have an index_html object at instantiation time
        self.failIf(self.folder.hasIndexHtml())

    def testHasIndexHtml(self):
        # Make sure we can determine if a container contains a index_html object
        self.folder.invokeFactory('Document', 'index_html', 
                                  title='Test index')
        self.failUnless(self.folder.hasIndexHtml())

    def testGetSelectableViewsWithViews(self):
        # Assume folders have at least two possible views to chose from
        views = self.folder.getSelectableViews()
        self.failUnless(views)
        self.failUnless('folder_listing' in views)
        self.failUnless('atct_album_view' in views)

    def testGetSelectableViewsWithoutViews(self):
        # Assume documents have only one view
        self.folder.invokeFactory('Document', 'test', 
                                  title='Test default page')
        doc = getattr(self.folder, 'test')
        self.failIf(doc.getSelectableViews())

    def testSetDefaultPageWithoutPage(self):
        # Make sure we can't define a default page if no object in folder
        self.failUnless(self.folder.canSelectDefaultPage())

    def testSetDefaultPageWithPage(self):
        # Make sure we can define a Document as default page
        self.folder.invokeFactory('Document', 'test', 
                                  title='Test default page')
        self.failUnless(self.folder.canSelectDefaultPage())
        self.folder.saveDefaultPage('test')
        self.failUnless(self.folder.test.isDefaultPageInFolder())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTemplateMixinScripts))
    return suite

if __name__ == '__main__':
    framework()
