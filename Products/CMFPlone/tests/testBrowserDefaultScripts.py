# -*- coding: utf-8 -*-
from plone.app.testing.bbb import PloneTestCase


class TestBrowserDefaultScripts(PloneTestCase):
    """Tests the browser default and folder-default page scripts"""

    def testSetDefaultPageWithoutPage(self):
        # Make sure we can't define a default page if no object in folder
        self.assertTrue(self.folder.canSelectDefaultPage())
