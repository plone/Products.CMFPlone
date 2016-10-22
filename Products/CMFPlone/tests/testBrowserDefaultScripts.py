# -*- coding: utf-8 -*-
from plone.app.testing.bbb import PloneTestCase


class TestBrowserDefaultScripts(PloneTestCase):
    """Tests the browser default and folder-default page scripts"""

    def testNoIndexHtml(self):
        # A folder shouldn't have an index_html object at instantiation time
        self.assertFalse(self.folder.hasIndexHtml())

    def testHasIndexHtml(self):
        # Make sure we can determine if a container contains a index_html
        # object
        self.folder.invokeFactory('Document', 'index_html',
                                  title='Test index')
        self.assertTrue(self.folder.hasIndexHtml())

    def testSetDefaultPageWithoutPage(self):
        # Make sure we can't define a default page if no object in folder
        self.assertTrue(self.folder.canSelectDefaultPage())
