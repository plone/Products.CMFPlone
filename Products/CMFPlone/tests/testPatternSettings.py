from Products.CMFPlone.tests import PloneTestCase
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ITinyMCESchema
from Products.CMFPlone.patterns import PloneSettingsAdapter
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
import json


class TestTinyMCESettings(PloneTestCase.PloneTestCase):

    def get_conf(self):
        adapter = PloneSettingsAdapter(self.portal, self.layer['request'], None)
        return json.loads(adapter.tinymce()['data-pat-tinymce'])

    def test_atd_included(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITinyMCESchema, prefix="plone")
        settings.libraries_spellchecker_choice = 'AtD'
        login(self.portal, TEST_USER_NAME)
        conf = self.get_conf()
        self.assertTrue('compat3x' in conf['tiny']['plugins'])
        self.assertTrue('AtD' in conf['tiny']['external_plugins'])

    def test_style_formats(self):
        conf = self.get_conf()
        self.assertEqual(len(conf['tiny']['style_formats']), 5)