from plone.base.interfaces import IEditingSchema
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class EditingRegistryIntegrationTest(unittest.TestCase):
    """Tests that the editing settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IEditingSchema, prefix="plone")

    def test_editing_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="editing-controlpanel"
        )
        self.assertTrue(view())

    def test_editing_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue(
            "EditingSettings"
            in [a.getAction(self)["id"] for a in self.controlpanel.listActions()]
        )

    def test_default_editor_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, "default_editor"))

    def test_ext_editor_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, "ext_editor"))

    def test_enable_link_integrity_checks_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, "enable_link_integrity_checks"))

    def test_lock_on_ttw_edit_attribute_exists(self):
        self.assertTrue(hasattr(self.settings, "lock_on_ttw_edit"))
