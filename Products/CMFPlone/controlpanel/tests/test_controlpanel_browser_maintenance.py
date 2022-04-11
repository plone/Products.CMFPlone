from pkg_resources import get_distribution
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.base.interfaces import IMaintenanceSchema
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from plone.testing.zope import login
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getAdapter
from zope.component import getUtility

import unittest


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
        login(self.app['acl_users'], 'app')

        import transaction
        transaction.commit()
        self.browser.addHeader(
            'Authorization',
            'Basic {}:{}'.format('app', 'secret')
        )

        self.site_administrator_browser = Browser(self.app)
        self.site_administrator_browser.handleErrors = False
        self.site_administrator_browser.addHeader(
            'Authorization',
            f'Basic {TEST_USER_NAME}:{TEST_USER_PASSWORD}'
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
        self.assertTrue(
            self.browser.url.endswith('/plone/@@overview-controlpanel')
        )

    def test_maintenance_control_panel_raises_unauthorized(self):
        self.site_administrator_browser.open(
            self.portal_url + '/@@maintenance-controlpanel')
        self.assertTrue(
            'You are not allowed to manage the Zope server.'
            in self.site_administrator_browser.contents)

    def test_maintenance_pack_database(self):
        """While we cannot test the actual packaging during tests, we can skip
           the actual manage_pack method by providing a negative value for
           days.
        """
        self.browser.open(self.portal_url + '/@@maintenance-controlpanel')
        db = self.portal._p_jar.db()
        original_pack = db.pack

        def pack(self, t=None, days=0):
            pass
        db.pack = pack

        self.browser.getControl(name='form.widgets.days').value = '0'
        self.browser.getControl(name="form.buttons.pack").click()
        self.assertTrue(self.browser.url.endswith('maintenance-controlpanel'))
        self.assertTrue('Packed the database.' in self.browser.contents)
        db.pack = original_pack


class MaintenanceControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.maintenance_settings = registry.forInterface(
            IMaintenanceSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(
            getAdapter(self.portal, IMaintenanceSchema)
        )

    def test_get_days(self):
        self.assertEqual(
            getAdapter(self.portal, IMaintenanceSchema).days,
            7
        )
        self.maintenance_settings.days = 4
        self.assertEqual(
            getAdapter(self.portal, IMaintenanceSchema).days,
            4
        )

    def test_set_days(self):
        self.assertEqual(
            self.maintenance_settings.days,
            7
        )
        getAdapter(self.portal, IMaintenanceSchema).days = 4
        self.assertEqual(
            self.maintenance_settings.days,
            4
        )
