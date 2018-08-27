# -*- coding: utf-8 -*-
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.interfaces.resources import (
    OVERRIDE_RESOURCE_DIRECTORY_NAME,
)
from zope.component import getUtility

from Products.CMFPlone.resources.browser.combine import (
    PRODUCTION_RESOURCE_DIRECTORY,
    combine_bundles,
)
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class ProductsCMFPloneSetupTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        combine_bundles(self.portal)
        persistent_directory = getUtility(
            IResourceDirectory, name="persistent")
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        self.production_folder = container[PRODUCTION_RESOURCE_DIRECTORY]

    def test_production_directory(self):
        self.assertEqual(
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
            b"jQuery",
            self.production_folder.readFile('default.js')
        )

    def test_overrides(self):
        persistent_directory = getUtility(
            IResourceDirectory, name="persistent")
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        container.makeDirectory('static')
        static = container['static']
        static.writeFile('plone-legacy-compiled.js', 'alert("Overrided legacy!");')
        combine_bundles(self.portal)
        self.assertIn(
            b'alert("Overrided legacy!");',
            self.production_folder.readFile('default.js')
        )
