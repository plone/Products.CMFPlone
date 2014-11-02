import unittest
from plone.app.testing import setRoles
from Products.CMFPlone.interfaces import IMaintenanceSchema
from zope.component import getAdapter
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING


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
        self.assertEquals(
            getAdapter(self.portal, IMaintenanceSchema).days,
            4
        )

    def test_set_days(self):
        self.assertEquals(
            self.maintenance_settings.days,
            7
        )
        getAdapter(self.portal, IMaintenanceSchema).days = 4
        self.assertEquals(
            self.maintenance_settings.days,
            4
        )
