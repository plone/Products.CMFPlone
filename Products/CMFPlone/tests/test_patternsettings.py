from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ITinyMCESchema
from Products.CMFPlone.patterns.view import PatternsSettingsView
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getUtility

import json
import unittest


class TestTinyMCESettings(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def get_conf(self):
        from Products.CMFPlone.patterns.settings import PatternSettingsAdapter
        adapter = PatternSettingsAdapter(
            self.layer['portal'],
            self.layer['request'],
            None
        )
        return json.loads(adapter.tinymce()['data-pat-tinymce'])

    def test_atd_included(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITinyMCESchema, prefix="plone")
        settings.libraries_spellchecker_choice = 'AtD'
        login(self.layer['portal'], TEST_USER_NAME)
        conf = self.get_conf()
        self.assertTrue('compat3x' in conf['tiny']['plugins'])
        self.assertTrue('AtD' in conf['tiny']['external_plugins'])

    def test_style_formats(self):
        conf = self.get_conf()
        self.assertEqual(len(conf['tiny']['style_formats']), 5)

    def test_other_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITinyMCESchema, prefix="plone")
        settings.other_settings = '{"foo": "bar"}'
        conf = self.get_conf()
        self.assertEqual(conf['tiny']['foo'], 'bar')


class TestPatternSettingsView(unittest.TestCase):
    """Ensure that the basic redirector setup is successful.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.layer['portal'].invokeFactory('Folder', 'folder')
        self.folder = self.layer['portal']['folder']

    def testShouldReturnCorrectType(self):
        settings = PatternsSettingsView(self.folder, self.layer['request'])
        result = settings()
        self.assertEqual(type(result), dict)
        for key, value in result.items():
            self.assertTrue(isinstance(key, str))
            self.assertTrue(isinstance(value, str))

    def testFolderUrls(self):
        settings = PatternsSettingsView(self.folder, self.layer['request'])
        result = settings()
        self.assertEqual(
            result['data-base-url'],
            self.folder.absolute_url()
        )
        self.assertEqual(
            result['data-portal-url'],
            self.layer['portal'].absolute_url()
        )
        self.assertEqual(
            result['data-view-url'],
            self.folder.absolute_url()
        )

    def testFileUrls(self):
        self.folder.invokeFactory('File', 'file1')
        file_obj = self.folder['file1']
        settings = PatternsSettingsView(file_obj, self.layer['request'])
        result = settings()
        self.assertEqual(result['data-base-url'], file_obj.absolute_url())
        self.assertEqual(
            result['data-portal-url'],
            self.layer['portal'].absolute_url()
        )
        self.assertEqual(
            result['data-view-url'],
            file_obj.absolute_url() + '/view'
        )

    def testPatternOptions(self):
        registry = getUtility(IRegistry)
        registry['plone.patternoptions'] = {
            'foo': '{"foo": "bar"}'
        }

        settings = PatternsSettingsView(self.folder, self.layer['request'])
        result = settings()
        self.assertEqual(result['data-pat-foo'], '{"foo": "bar"}')
