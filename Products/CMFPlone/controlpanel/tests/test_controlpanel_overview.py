# -*- coding: utf-8 -*-
from datetime import date
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import mock
import unittest


def mock_getUtility1(iface):
    return {}


def mock_getUtility2(iface):
    return {'plone.portal_timezone': None}


def mock_getUtility3(iface):
    return {'plone.portal_timezone': 'Europe/Amsterdam'}


def mock_getUtility4(iface):
    return {'plone.app.event.portal_timezone': 'Europe/Amsterdam'}


class MockVersionInfo(object):
    def __init__(self, major, minor, micro=0):
        self.major = major
        self.minor = minor
        self.micro = micro


mock_python2 = MockVersionInfo(2, 7)
mock_python36 = MockVersionInfo(3, 6)
mock_python37 = MockVersionInfo(3, 7)
mock_python38 = MockVersionInfo(3, 8)
mock_python39 = MockVersionInfo(3, 9)


class MockDate(object):

    def __init__(self, today):
        self._today = today

    def today(self):
        return self._today


class TestControlPanel(unittest.TestCase):

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    @mock.patch('sys.version_info',
                new=mock_python2)
    def test_python2_warning(self):
        # Test the warnings that get shows when using Python 2.7.
        # Python 2 should only be used temporarily, so we always warn.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertTrue(view.python2_warning())
        self.assertFalse(view.python_warning())
        self.assertTrue(view.version_warning())
        self.assertIn("You are using Python 2.", view())

    @mock.patch('sys.version_info',
                new=mock_python36)
    def test_python36_warning(self):
        # Test the warnings that get shows when using Python 3.6.
        # Python 3.6 is already end-of-life at the time of writing this test,
        # so we always warn.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertFalse(view.python2_warning())
        self.assertTrue(view.python_warning())
        self.assertTrue(view.version_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    # We want to mock datetime.date.today, but that gives a TypeError:
    # can't set attributes of built-in/extension type 'datetime.date'
    # So use a class as wrapper, and patch the date used in the module.
    @mock.patch('sys.version_info',
                new=mock_python37)
    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.date',
                new=MockDate(date(2023, 6, 1)))
    def test_python37_warning_early(self):
        # Test the warnings that get shows when using Python 3.7.
        # This depends on the date.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertFalse(view.python2_warning())
        self.assertFalse(view.python_warning())
        self.assertFalse(view.version_warning())

    @mock.patch('sys.version_info',
                new=mock_python37)
    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.date',
                new=MockDate(date(2023, 7, 1)))
    def test_python37_warning_late(self):
        # Test the warnings that get shows when using Python 3.7.
        # This depends on the date.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertFalse(view.python2_warning())
        self.assertTrue(view.python_warning())
        self.assertTrue(view.version_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch('sys.version_info',
                new=mock_python38)
    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.date',
                new=MockDate(date(2024, 10, 1)))
    def test_python38_warning_early(self):
        # Test the warnings that get shows when using Python 3.8.
        # This depends on the date.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertFalse(view.python2_warning())
        self.assertFalse(view.python_warning())
        # We *do* already get a warning for a different reason:
        # Plone 5.2 is out of maintenance support.
        self.assertTrue(view.version_warning())

    @mock.patch('sys.version_info',
                new=mock_python38)
    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.date',
                new=MockDate(date(2024, 11, 1)))
    def test_python38_warning_late(self):
        # Test the warnings that get shows when using Python 3.8.
        # This depends on the date.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertFalse(view.python2_warning())
        self.assertTrue(view.python_warning())
        self.assertTrue(view.version_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch('sys.version_info',
                new=mock_python39)
    def test_python39_warning(self):
        # Test the warnings that get shows when using Python 3.9.
        # 3.9 is too new, so we always warn.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertFalse(view.python2_warning())
        self.assertTrue(view.python_warning())
        self.assertTrue(view.version_warning())
        self.assertIn("You are using a Python version that is not supported.", view())

    @mock.patch('sys.version_info',
                new=mock_python38)
    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.date',
                new=MockDate(date(2023, 10, 1)))
    def test_plone_warnings_early(self):
        # Test the warnings that get shows for the Plone version itself.
        # This depends on the date.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertFalse(view.plone_maintenance_warning())
        self.assertFalse(view.plone_security_warning())
        self.assertFalse(view.version_warning())

    @mock.patch('sys.version_info',
                new=mock_python38)
    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.date',
                new=MockDate(date(2024, 10, 1)))
    def test_plone_warnings_middle(self):
        # Test the warnings that get shows for the Plone version itself.
        # This depends on the date.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertTrue(view.plone_maintenance_warning())
        self.assertFalse(view.plone_security_warning())
        self.assertTrue(view.version_warning())
        self.assertIn(
            "You are using a Plone version that is out of maintenance support.",
            view(),
        )

    @mock.patch('sys.version_info',
                new=mock_python38)
    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.date',
                new=MockDate(date(2024, 11, 1)))
    def test_plone_warnings_late(self):
        # Test the warnings that get shows for the Plone version itself.
        # This depends on the date.
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertTrue(view.plone_maintenance_warning())
        self.assertTrue(view.plone_security_warning())
        self.assertTrue(view.version_warning())
        self.assertIn(
            "You are using a Plone version that is out of security support.",
            view(),
        )

    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.getUtility',
                new=mock_getUtility1)
    def test_timezone_warning__noreg(self):
        # If no registry key is available, return True
        registry = getUtility(IRegistry)
        reg_key = "plone.portal_timezone"
        del registry.records[reg_key]
        self.assertFalse(reg_key in registry)
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertTrue(view.timezone_warning())

    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.getUtility',
                new=mock_getUtility2)
    def test_timezone_warning__emptyreg(self):
        # If registry key value is empty, return True
        registry = getUtility(IRegistry)
        reg_key = "plone.portal_timezone"
        registry[reg_key] = None
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertTrue(view.timezone_warning())

    @mock.patch('Products.CMFPlone.controlpanel.browser.overview.getUtility',
                new=mock_getUtility3)
    def test_timezone_warning__set(self):
        # If new plone.portal_timezone is set, return False
        view = self.portal.restrictedTraverse('@@overview-controlpanel')
        self.assertFalse(view.timezone_warning())
