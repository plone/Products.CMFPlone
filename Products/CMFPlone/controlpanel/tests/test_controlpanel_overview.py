from datetime import date
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from unittest import mock
from zope.component import getUtility

import unittest


def mock_getUtility1(iface):
    return {}


def mock_getUtility2(iface):
    return {"plone.portal_timezone": None}


def mock_getUtility3(iface):
    return {"plone.portal_timezone": "Europe/Amsterdam"}


def mock_getUtility4(iface):
    return {"plone.app.event.portal_timezone": "Europe/Amsterdam"}


class MockVersionInfo:
    def __init__(self, major, minor, micro=0):
        self.major = major
        self.minor = minor
        self.micro = micro


mock_python38 = MockVersionInfo(3, 8)
mock_python39 = MockVersionInfo(3, 9)
mock_python310 = MockVersionInfo(3, 10)
mock_python311 = MockVersionInfo(3, 11)
mock_python312 = MockVersionInfo(3, 12)
mock_python313 = MockVersionInfo(3, 13)
mock_python314 = MockVersionInfo(3, 14)


class MockDate:
    def __init__(self, today):
        self._today = today

    def today(self):
        return self._today


class TestControlPanel(unittest.TestCase):
    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_version_warning(self):
        # We always get a warning: Plone 6.0 is out of maintenance support.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.version_warning())

    @mock.patch("sys.version_info", new=mock_python38)
    def test_python38_warning(self):
        # Test the warnings that get shown when using Python 3.8.
        # Python 3.8 is already end-of-life at the time of writing this test,
        # so we always warn.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch("sys.version_info", new=mock_python39)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2025, 4, 1)),
    )
    def test_python39_warning_early(self):
        # Test the warnings that get shown when using Python 3.9.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.python_warning())

    @mock.patch("sys.version_info", new=mock_python39)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2025, 11, 1)),
    )
    def test_python39_warning_late(self):
        # Test the warnings that get shown when using Python 3.9.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch("sys.version_info", new=mock_python310)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2025, 4, 1)),
    )
    def test_python310_warning_early(self):
        # Test the warnings that get shown when using Python 3.10.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.python_warning())

    @mock.patch("sys.version_info", new=mock_python310)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2026, 11, 1)),
    )
    def test_python310_warning_late(self):
        # Test the warnings that get shown when using Python 3.10.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch("sys.version_info", new=mock_python311)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2025, 4, 1)),
    )
    def test_python311_warning_early(self):
        # Test the warnings that get shown when using Python 3.11.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.python_warning())

    @mock.patch("sys.version_info", new=mock_python311)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2027, 11, 1)),
    )
    def test_python311_warning_late(self):
        # Test the warnings that get shown when using Python 3.11.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch("sys.version_info", new=mock_python312)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2025, 4, 1)),
    )
    def test_python312_warning_early(self):
        # Test the warnings that get shown when using Python 3.12.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.python_warning())

    @mock.patch("sys.version_info", new=mock_python312)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2028, 12, 1)),
    )
    def test_python312_warning_late(self):
        # Test the warnings that get shown when using Python 3.12.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch("sys.version_info", new=mock_python313)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2025, 4, 1)),
    )
    def test_python313_warning_early(self):
        # Test the warnings that get shown when using Python 3.13.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.python_warning())

    @mock.patch("sys.version_info", new=mock_python313)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2029, 11, 1)),
    )
    def test_python313_warning_late(self):
        # Test the warnings that get shown when using Python 3.13.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch("sys.version_info", new=mock_python314)
    def test_python314_warning(self):
        # Test the warnings that get shown when using Python 3.14.
        # 3.14 is too new, so we always warn.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertTrue(view.version_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

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
