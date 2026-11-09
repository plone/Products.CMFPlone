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


class MockSys:
    # Only mock sys in the overview module, not sys.version_info globally:
    # Chameleon compares sys.version_info with a tuple when compiling
    # a template, which fails with our MockVersionInfo.
    def __init__(self, major, minor, micro=0):
        self.version_info = MockVersionInfo(major, minor, micro)


class MockDate:
    def __init__(self, today):
        self._today = today

    def today(self):
        return self._today


PYTHON_WARNING = "You are using a Python version that is not supported."
MAINTENANCE_WARNING = (
    "You are using a Plone version that is out of maintenance support."
)
SECURITY_WARNING = "You are using a Plone version that is out of security support."
RELEASE_SCHEDULE = "Plone release schedule"

# Test cases for the version warnings.  Each case becomes a subtest.
# Keys: py is the Python 3 minor version, today is the mocked current date,
# python and security are the expected Python and Plone security warnings.
# Plone 6.2 has no end date for maintenance support yet,
# so we never expect a maintenance warning.
# Security support for Plone 6.2 ends after 2027-12-31.
VERSION_WARNING_CASES = (
    # Python 3.10 is supported until 2026-10-01.
    {"py": 10, "today": date(2025, 4, 1), "python": False, "security": False},
    {"py": 10, "today": date(2026, 11, 1), "python": True, "security": False},
    # Python 3.11 is supported until 2027-10-01.
    {"py": 11, "today": date(2025, 4, 1), "python": False, "security": False},
    {"py": 11, "today": date(2027, 11, 1), "python": True, "security": False},
    # Python 3.12 is supported until 2028-10-01.
    # Use it to test the end of Plone security support.
    {"py": 12, "today": date(2025, 4, 1), "python": False, "security": False},
    {"py": 12, "today": date(2026, 11, 1), "python": False, "security": False},
    {"py": 12, "today": date(2027, 12, 31), "python": False, "security": False},
    {"py": 12, "today": date(2028, 1, 1), "python": False, "security": True},
    {"py": 12, "today": date(2028, 12, 1), "python": True, "security": True},
    # Python 3.13 is supported until 2029-10-01.
    {"py": 13, "today": date(2025, 4, 1), "python": False, "security": False},
    {"py": 13, "today": date(2029, 11, 1), "python": True, "security": True},
    # Python 3.14 is supported until 2030-10-01.
    # Test the day before, on, and after the deadline.
    {"py": 14, "today": date(2030, 9, 30), "python": False, "security": True},
    {"py": 14, "today": date(2030, 10, 1), "python": True, "security": True},
    {"py": 14, "today": date(2030, 10, 2), "python": True, "security": True},
    # Python 3.15 is supported until 2031-10-01.
    {"py": 15, "today": date(2026, 11, 1), "python": False, "security": False},
    {"py": 15, "today": date(2031, 11, 1), "python": True, "security": True},
    # Python 3.16 is not supported at all.
    {"py": 16, "today": date(2026, 11, 1), "python": True, "security": False},
)


class TestControlPanel(unittest.TestCase):
    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_version_warnings(self):
        # Each case is a subtest, so when one case fails, the others still run.
        for case in VERSION_WARNING_CASES:
            with self.subTest(**case):
                with mock.patch(
                    "Products.CMFPlone.controlpanel.browser.overview.sys",
                    new=MockSys(3, case["py"]),
                ), mock.patch(
                    "Products.CMFPlone.controlpanel.browser.overview.date",
                    new=MockDate(case["today"]),
                ):
                    self.check_version_warnings(case["python"], case["security"])

    def check_version_warnings(self, python, security):
        # Compare all results at once, so a failure shows every difference.
        # Show the full diff, even when many values differ.
        self.maxDiff = None
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        html = view()
        actual = {
            "python_warning()": view.python_warning(),
            "plone_maintenance_warning()": view.plone_maintenance_warning(),
            "plone_security_warning()": view.plone_security_warning(),
            "version_warning()": view.version_warning(),
            "Python warning shown": PYTHON_WARNING in html,
            "maintenance warning shown": MAINTENANCE_WARNING in html,
            "security warning shown": SECURITY_WARNING in html,
            "release schedule link shown": RELEASE_SCHEDULE in html,
        }
        expected = {
            "python_warning()": python,
            "plone_maintenance_warning()": False,
            "plone_security_warning()": security,
            "version_warning()": python or security,
            "Python warning shown": python,
            "maintenance warning shown": False,
            "security warning shown": security,
            "release schedule link shown": python or security,
        }
        self.assertEqual(actual, expected)

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
        # gunicorn is usually not installed, so mock its distribution.
        # Otherwise we get a warning that its version cannot be found.
        with mock.patch(
            "Products.CMFPlone.controlpanel.browser.overview.distribution",
            return_value=mock.Mock(version="19.6.0"),
        ) as distribution:
            info = view.server_info()
        distribution.assert_called_once_with("gunicorn")
        self.assertEqual(info["server_name"], "gunicorn")
        self.assertEqual(info["version"], "19.6.0")
        self.request["SERVER_SOFTWARE"] = "bad-gunicorn-name/19.6.0"
        view = self.portal.restrictedTraverse("@@overview-controlpanel")
        with self.assertWarns(Warning):
            view.server_info()["server_name"]
