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
from Products.GenericSetup.tests import common


class DummyImportContext(common.DummyImportContext):
    # Copied from plone.app.registry tests.
    # This expands the context with directories.

    _directories = {}

    def listDirectory(self, path):
        return self._directories.get(path, [])

    def isDirectory(self, path):
        return path in self._directories


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

    def test_overrides(self):
        persistent_directory = getUtility(
            IResourceDirectory, name="persistent")
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        container.makeDirectory('static')
        static = container['static']
        static.writeFile('plone-legacy-compiled.js', 'alert("Overrided legacy!");')
        combine_bundles(self.portal)
        self.assertIn(
            'alert("Overrided legacy!");',
            self.production_folder.readFile('default.js')
        )

    def test_import(self):
        # If IBundleRegistry is in registry.xml, the combine-bundles import step
        # will call combine_bundles.
        from Products.CMFPlone.resources.exportimport.bundles import combine
        # from Products.CMFPlone.resources.browser.combine import get_override_directory
        # from Products.CMFPlone.resources.browser.combine import PRODUCTION_RESOURCE_DIRECTORY

        # Prepare some registry xml files with or without the key IBundleRegistry.
        xml_with = '<registry>with IBundleRegistry</registry>'
        xml_without = '<registry>without bundle registry</registry>'
        xml_without2 = '<registry>without bundle registry</registry>'
        context = DummyImportContext(self.portal, purge=False)

        def get_timestamp():
            # If combine_bundles is run, a timestamp is updated.
            return self.production_folder.readFile('timestamp.txt')

        ts1 = get_timestamp()
        self.assertTrue(ts1)

        # call the import step on a file without bundles
        context._files = {'registry.xml': xml_without}
        combine(context)
        ts2 = get_timestamp()
        self.assertEqual(ts1, ts2)

        # call the import step on a file with bundles
        context._files = {'registry.xml': xml_with}
        combine(context)
        ts3 = get_timestamp()
        self.assertLess(ts2, ts3)

        # call the import step on a file without bundles
        context._files = {'registry.xml': xml_without2}
        combine(context)
        ts4 = get_timestamp()
        self.assertEqual(ts3, ts4)

        # Since Plone 5.1 the registry xml can also be a directory.
        # Set one file with bundles.
        context._files = {
            'registry.xml': xml_without,
            'registry/foo2.xml': xml_with,
            'registry/foo3.xml': xml_without2,
        }
        context._directories = {
            'registry': [
                'foo2.xml',
                'foo3.xml',
            ]
        }
        combine(context)
        ts10 = get_timestamp()
        self.assertLess(ts4, ts10)

        # The registry.xml file itself may be missing.
        context._files = {
            'registry/foo2.xml': xml_with,
            'registry/foo3.xml': xml_without2,
        }
        combine(context)
        ts11 = get_timestamp()
        self.assertLess(ts10, ts11)

        # Now without any bundle info.
        context._files = {
            'registry/foo2.xml': xml_without,
            'registry/foo3.xml': xml_without2,
        }
        combine(context)
        ts12 = get_timestamp()
        self.assertEqual(ts11, ts12)
