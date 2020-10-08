from Products.CMFPlone.interfaces import IEditingSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getAdapter
from zope.component import getUtility
import unittest


class EditingControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IEditingSchema, prefix='plone')

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, IEditingSchema))

    def test_get_enable_link_integrity_checks_setting(self):
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).enable_link_integrity_checks,  # noqa
            True
        )
        self.settings.enable_link_integrity_checks = False
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).enable_link_integrity_checks,  # noqa
            False
        )

    def test_set_enable_link_integrity_checks_setting(self):
        self.assertEqual(
            self.settings.enable_link_integrity_checks,
            True
        )
        getAdapter(self.portal, IEditingSchema).enable_link_integrity_checks = False  # noqa
        self.assertEqual(
            self.settings.enable_link_integrity_checks,
            False
        )

    def test_get_ext_editor_setting(self):
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).ext_editor,
            False
        )
        self.settings.ext_editor = True
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).ext_editor,
            True
        )

    def test_set_ext_editor_setting(self):
        self.assertEqual(
            self.settings.ext_editor,
            False
        )
        getAdapter(self.portal, IEditingSchema).ext_editor = True
        self.assertEqual(
            self.settings.ext_editor,
            True
        )

    def test_get_default_editor_setting(self):
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).default_editor,
            'TinyMCE'
        )
        self.settings.default_editor = 'None'
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).default_editor,
            'None'
        )

    def test_set_default_editor_setting(self):
        self.assertEqual(
            self.settings.default_editor,
            'TinyMCE'
        )
        getAdapter(self.portal, IEditingSchema).default_editor = 'None'
        self.assertEqual(
            self.settings.default_editor,
            'None'
        )

    def test_get_lock_on_ttw_edit_setting(self):
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).lock_on_ttw_edit,
            True
        )
        self.settings.lock_on_ttw_edit = False
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).lock_on_ttw_edit,
            False
        )

    def test_set_lock_on_ttw_edit_setting(self):
        self.assertEqual(
            self.settings.lock_on_ttw_edit,
            True
        )
        getAdapter(self.portal, IEditingSchema).lock_on_ttw_edit = False
        self.assertEqual(
            self.settings.lock_on_ttw_edit,
            False
        )
