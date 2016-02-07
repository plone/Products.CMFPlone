# -*- coding: utf-8 -*-
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
import unittest2 as unittest
from App.ApplicationManager import ApplicationManager
from pkg_resources import get_distribution

has_zope4 = get_distribution('Zope2').version.startswith('4')


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
        # we have to create a user on the zope root. this just does not work
        # with plone.app.testing and TEST_USER or SITE_OWNER
        self.app.acl_users.userFolderAddUser('app', 'secret', ['Manager'], [])
        from plone.testing import z2
        z2.login(self.app['acl_users'], 'app')

        import transaction
        transaction.commit()
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % ('app', 'secret')
        )

        self.site_administrator_browser = Browser(self.app)
        self.site_administrator_browser.handleErrors = False
        self.site_administrator_browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD,)
        )

    def test_maintenance_control_panel_link(self):
        self.browser.open(
            "%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('Editing').click()

    def test_maintenance_control_panel_backlink(self):
        self.browser.open(
            "%s/@@maintenance-controlpanel" % self.portal_url)
        self.assertTrue("Advanced" in self.browser.contents)

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

    @unittest.skipIf(has_zope4, 'Broken with zope4. Reason yet unknown.')
    def test_maintenance_pack_database(self):
        """While we cannot test the actual packaging during tests, we can skip
           the actual manage_pack method by providing a negative value for
           days.
        """
        self.browser.open(self.portal_url + '/@@maintenance-controlpanel')
        original_pack = ApplicationManager.manage_pack

        def manage_pack(self, days=0, REQUEST=None, _when=None):
            pass
        ApplicationManager.manage_pack = manage_pack

        self.browser.getControl(name='form.widgets.days').value = '0'
        self.browser.getControl(name="form.buttons.pack").click()
        self.assertTrue(self.browser.url.endswith('maintenance-controlpanel'))
        self.assertTrue('Packed the database.' in self.browser.contents)
        ApplicationManager.manage_pack = original_pack
