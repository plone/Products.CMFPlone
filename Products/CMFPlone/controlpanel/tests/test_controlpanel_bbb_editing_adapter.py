import unittest
from plone.app.testing import setRoles
from zope.component import getAdapter
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.testing import TEST_USER_ID

from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING

from Products.CMFPlone.interfaces import IEditingSchema


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

    def test_get_visible_ids(self):
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).visible_ids,
            False
        )
        self.settings.visible_ids = True
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).visible_ids,
            True
        )

    def test_set_visible_ids(self):
        self.assertEqual(
            self.settings.visible_ids,
            False
        )
        getAdapter(self.portal, IEditingSchema).visible_ids = True
        self.assertEqual(
            self.settings.visible_ids,
            True
        )

    def test_get_enable_link_integrity_checks_setting(self):
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).enable_link_integrity_checks,
            True
        )
        self.settings.enable_link_integrity_checks = False
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).enable_link_integrity_checks,
            False
        )

    def test_set_enable_link_integrity_checks_setting(self):
        self.assertEqual(
            self.settings.enable_link_integrity_checks,
            True
        )
        getAdapter(self.portal, IEditingSchema).enable_link_integrity_checks = False
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
            u'TinyMCE'
        )
        self.settings.default_editor = u'None'
        self.assertEqual(
            getAdapter(self.portal, IEditingSchema).default_editor,
            u'None'
        )

    def test_set_default_editor_setting(self):
        self.assertEqual(
            self.settings.default_editor,
            u'TinyMCE'
        )
        getAdapter(self.portal, IEditingSchema).default_editor = u'None'
        self.assertEqual(
            self.settings.default_editor,
            u'None'
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
