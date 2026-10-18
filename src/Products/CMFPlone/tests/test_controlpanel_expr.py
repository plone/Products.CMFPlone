from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.globalrequest import setRequest

import unittest


class TestControlPanelExpressions(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.cp = getToolByName(self.portal, "portal_controlpanel")
        self.folder = self.portal["test-folder"]

    def test_enum_configlets_uses_plone_context_state_on_portal(self):
        # This condition uses plone_context_state which is provided by the new _getExprContext
        # is_portal_root() will be true on portal root.
        self.cp.addAction(
            id="test-configlet",
            name="Test Configlet",
            action="string:test",
            condition="python:plone_context_state.is_portal_root()",
            permission="cmf.ManagePortal",
            category="Plone",
            visible=True,
        )

        self.request.set("PARENTS", [self.portal])
        setRequest(self.request)

        configlets = [c["id"] for c in self.cp.enumConfiglets(group="Plone")]
        self.assertIn(
            "test-configlet", configlets, "Configlet should be visible on portal root"
        )

    def test_enum_configlets_uses_plone_context_state_on_folder(self):
        # This condition uses plone_context_state which is provided by the new _getExprContext
        # is_portal_root() will be false on the folder.
        self.cp.addAction(
            id="test-configlet",
            name="Test Configlet",
            action="string:test",
            condition="python:plone_context_state.is_portal_root()",
            permission="cmf.ManagePortal",
            category="Plone",
            visible=True,
        )

        self.request.set("PARENTS", [self.folder, self.portal])
        setRequest(self.request)

        configlets = [c["id"] for c in self.cp.enumConfiglets(group="Plone")]
        self.assertNotIn(
            "test-configlet", configlets, "Configlet should NOT be visible on folder"
        )

    def test_enum_configlets_uses_plone_portal_state(self):
        # This condition uses plone_portal_state
        self.cp.addAction(
            id="test-configlet-2",
            name="Test Configlet 2",
            action="string:test",
            condition="python:plone_portal_state.portal_url() is not None",
            permission="cmf.ManagePortal",
            category="Plone",
            visible=True,
        )

        self.request.set("PARENTS", [self.portal])
        setRequest(self.request)
        configlets = [c["id"] for c in self.cp.enumConfiglets(group="Plone")]
        self.assertIn(
            "test-configlet-2",
            configlets,
            "Configlet should be visible as plone_portal_state is available",
        )
