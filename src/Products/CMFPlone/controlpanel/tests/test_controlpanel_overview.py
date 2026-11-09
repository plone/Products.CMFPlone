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


mock_python310 = MockVersionInfo(3, 10)
mock_python311 = MockVersionInfo(3, 11)
mock_python312 = MockVersionInfo(3, 12)
mock_python313 = MockVersionInfo(3, 13)
mock_python314 = MockVersionInfo(3, 14)
mock_python315 = MockVersionInfo(3, 15)
mock_python316 = MockVersionInfo(3, 16)

PYTHON_WARNING = "You are using a Python version that is not supported."
MAINTENANCE_WARNING = (
    "You are using a Plone version that is out of maintenance support."
)
SECURITY_WARNING = "You are using a Plone version that is out of security support."


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

    @mock.patch("sys.version_info", new=mock_python312)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2026, 11, 1)),
    )
    def test_version_warning_none(self):
        # Plone 6.2 is still in maintenance support,
        # and Python 3.12 is still supported.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.python_warning())
        self.assertFalse(view.plone_maintenance_warning())
        self.assertFalse(view.plone_security_warning())
        self.assertFalse(view.version_warning())
        html = view()
        self.assertNotIn(PYTHON_WARNING, html)
        self.assertNotIn(MAINTENANCE_WARNING, html)
        self.assertNotIn(SECURITY_WARNING, html)
        self.assertNotIn("Plone release schedule", html)

    @mock.patch("sys.version_info", new=mock_python312)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2027, 12, 31)),
    )
    def test_plone_security_warning_on_deadline(self):
        # On the last day of security support, we do not warn yet.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.plone_security_warning())
        self.assertFalse(view.version_warning())

    @mock.patch("sys.version_info", new=mock_python312)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2028, 1, 1)),
    )
    def test_plone_security_warning_after_deadline(self):
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.plone_security_warning())
        self.assertTrue(view.version_warning())
        html = view()
        self.assertIn(SECURITY_WARNING, html)
        self.assertIn("Plone release schedule", html)
        self.assertNotIn(PYTHON_WARNING, html)

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
        self.assertIn(PYTHON_WARNING, view())

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
        self.assertIn(PYTHON_WARNING, view())

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
        self.assertIn(PYTHON_WARNING, view())

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
        self.assertIn(PYTHON_WARNING, view())

    @mock.patch("sys.version_info", new=mock_python314)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2030, 9, 30)),
    )
    def test_python314_warning_day_before(self):
        # The day before the end-of-life date, we do not warn yet.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.python_warning())

    @mock.patch("sys.version_info", new=mock_python314)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2030, 10, 1)),
    )
    def test_python314_warning_on_deadline(self):
        # On the end-of-life date itself, we warn.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())

    @mock.patch("sys.version_info", new=mock_python314)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2030, 10, 2)),
    )
    def test_python314_warning_after_deadline(self):
        # After the end-of-life date, we warn.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertIn(PYTHON_WARNING, view())

    @mock.patch("sys.version_info", new=mock_python315)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2026, 11, 1)),
    )
    def test_python315_warning_early(self):
        # Test the warnings that get shown when using Python 3.15.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertFalse(view.python_warning())

    @mock.patch("sys.version_info", new=mock_python315)
    @mock.patch(
        "Products.CMFPlone.controlpanel.browser.overview.date",
        new=MockDate(date(2031, 11, 1)),
    )
    def test_python315_warning_late(self):
        # Test the warnings that get shown when using Python 3.15.
        # This depends on the date.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertIn(PYTHON_WARNING, view())

    @mock.patch("sys.version_info", new=mock_python316)
    def test_python316_warning(self):
        # Python 3.16 is too new, so we always warn.
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        self.assertTrue(view.python_warning())
        self.assertTrue(view.version_warning())
        self.assertIn(PYTHON_WARNING, view())

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
