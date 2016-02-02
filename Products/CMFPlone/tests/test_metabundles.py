# -*- coding: utf-8 -*-
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.interfaces.resources import (
    OVERRIDE_RESOURCE_DIRECTORY_NAME,
)
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zope.component import getUtility

from Products.CMFPlone.resources.browser.combine import (
    PRODUCTION_RESOURCE_DIRECTORY,
    combine_bundles,
)


class ProductsCMFPloneSetupTest(PloneTestCase):

    def afterSetUp(self):
        combine_bundles(self.portal)
        persistent_directory = getUtility(
            IResourceDirectory, name="persistent")
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        self.production_folder = container[PRODUCTION_RESOURCE_DIRECTORY]

    def test_production_directory(self):
        self.assertEquals(
            self.production_folder.listDirectory(),
            [
                'default.css',
                'default.js',
                'logged-in.css',
                'logged-in.js',
                'timestamp.txt'
            ]
        )

    def test_default_js_bundle(self):
        self.assertIn(
            "jQuery",
            self.production_folder.readFile('default.js')
        )
