# -*- coding: utf-8 -*-
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import SITE_OWNER_NAME
from plone.testing.z2 import Browser
from plone.registry import Registry

import unittest2 as unittest

from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, setRoles

from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING


class MaintenanceControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the maintenance control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization',
                'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
            )
        self.site_administrator_browser = Browser(self.app)
        self.site_administrator_browser.handleErrors = False
        self.site_administrator_browser.addHeader('Authorization',
                'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,)
            )

    def test_maintenance_control_panel_link(self):
        self.browser.open(
            "%s/plone_control_panel" % self.portal_url)
        self.browser.getLink('Editing').click()

    def test_maintenance_control_panel_backlink(self):
        self.browser.open(
            "%s/@@maintenance-controlpanel" % self.portal_url)
        self.assertTrue("Plone Configuration" in self.browser.contents)

    def test_maintenance_control_panel_sidebar(self):
        self.browser.open(
            "%s/@@maintenance-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertEqual(
            self.browser.url,
            'http://nohost/plone/@@overview-controlpanel')

    def test_maintenance_control_panel_raises_unauthorized(self):
        self.site_administrator_browser.open(
            self.portal_url + '/@@maintenance-controlpanel')
        self.assertTrue(
            'You are not allowed to manage the Zope server.'
            in self.site_administrator_browser.contents)

    @unittest.skip('Not working yet.')
    def test_maintenance_pack_database(self):
        """While we cannot test the actual packaging during tests, we can skip
           the actual manage_pack method by providing a negative value for
           days.
        """
        self.browser.open(self.portal_url + '/@@maintenance-controlpanel')
        self.browser.getControl(name='form.widgets.days').value = '-1'
        self.browser.getControl(name="form.buttons.pack").click()
        self.assertTrue(self.browser.url.endswith('maintenance-controlpanel'))
        self.assertTrue('Packed the database.' in self.browser.contents)
