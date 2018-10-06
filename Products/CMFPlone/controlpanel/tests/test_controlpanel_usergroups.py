# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class TypesRegistryIntegrationTest(unittest.TestCase):
    """Tests that the types settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IUserGroupsSettingsSchema, prefix="plone"
        )

    @unittest.skip(
        'view rendering here results in a test-isolation problem together with'
        'plone.z3cform. To reproduce, test with:'
        './bin/test --layer plone.z3cform:Functional '
        '    --layer  Products.CMFPlone.testing.CMFPloneLayer:Integration  '
        '    -t plone.z3cform '
        '    -t Products.CMFPlone.controlpanel.tests.'
        'test_controlpanel_usergroups.TypesRegistryIntegrationTest'
    )
    def test_usergroups_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="usergroup-controlpanel"
        )
        self.assertTrue(view())

    def test_usergroups_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue(
            'UsersGroups'
            in [
                a.getAction(self)['id']
                for a in self.controlpanel.listActions()
            ]
        )

    def test_many_groups_setting(self):
        self.assertTrue(hasattr(self.settings, 'many_groups'))

    def test_many_users_setting(self):
        self.assertTrue(hasattr(self.settings, 'many_users'))
