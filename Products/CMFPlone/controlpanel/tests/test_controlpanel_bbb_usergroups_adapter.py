from plone.app.testing import setRoles
from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
from zope.component import getAdapter
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import unittest2 as unittest

from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING


class UserGroupsControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.usergroups_settings = registry.forInterface(
            IUserGroupsSettingsSchema, prefix="plone")

    def test_adapter_lookup(self):
        self.assertTrue(
            getAdapter(self.portal, IUserGroupsSettingsSchema)
        )

    def test_many_groups(self):
        getAdapter(self.portal, IUserGroupsSettingsSchema).set_many_groups(True)
        self.assertEqual(
            getAdapter(self.portal, IUserGroupsSettingsSchema).get_many_groups(),
            True
        )

    def test_many_users(self):
        getAdapter(self.portal, IUserGroupsSettingsSchema).set_many_users(True)
        self.assertEqual(
            getAdapter(self.portal, IUserGroupsSettingsSchema).get_many_users(),
            True
        )
