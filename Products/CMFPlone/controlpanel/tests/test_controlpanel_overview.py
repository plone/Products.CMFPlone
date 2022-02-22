from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from unittest import mock
import os
import unittest


def mock_getUtility1(iface):
    return {}


def mock_getUtility2(iface):
    return {"plone.portal_timezone": None}


def mock_getUtility3(iface):
    return {"plone.portal_timezone": "Europe/Amsterdam"}


def mock_getUtility4(iface):
    return {"plone.app.event.portal_timezone": "Europe/Amsterdam"}


class TestControlPanel(unittest.TestCase):

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.getUtility",
        new=mock_getUtility1,
    )
    def test_timezone_warning__noreg(self):
        # If no registry key is available, return True
        registry = getUtility(IRegistry)
        reg_key = "plone.portal_timezone"
        del registry.records[reg_key]
        self.assertFalse(reg_key in registry)
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.timezone_warning())

    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.getUtility",
        new=mock_getUtility2,
    )
    def test_timezone_warning__emptyreg(self):
        # If registry key value is empty, return True
        registry = getUtility(IRegistry)
        reg_key = "plone.portal_timezone"
        registry[reg_key] = None
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.timezone_warning())

    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.getUtility",
        new=mock_getUtility3,
    )
    def test_timezone_warning__set(self):
        # If new plone.portal_timezone is set, return False
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.timezone_warning())

    def test_gunicorn_server_name(self):
        self.request["SERVER_SOFTWARE"] = "gunicorn/19.6.0"
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertEqual(view.server_info()["server_name"], "gunicorn")
        self.request["SERVER_SOFTWARE"] = "bad-gunicorn-name/19.6.0"
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        with self.assertWarns(Warning):
            view.server_info()["server_name"]
