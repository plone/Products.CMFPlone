# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.testing.z2 import Browser
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

from plone.registry.interfaces import IRegistry
from plone.registry import Registry
from Products.CMFPlone.interfaces import IMarkupSchema

from zope.component import getMultiAdapter, getUtility

from Products.CMFCore.utils import getToolByName

from plone.app.testing import TEST_USER_ID, setRoles

from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING


class MarkupRegistryIntegrationTest(unittest.TestCase):
    """Test plone.app.registry based markup storage.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
#        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        registry = getUtility(IRegistry)
#        self.registry.registerInterface(IMarkupSchema)
        self.settings = registry.forInterface(
            IMarkupSchema, prefix="plone")

    def test_markup_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST),
            name="markup-controlpanel"
        )
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_plone_app_registry_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue(
            'plone.app.registry' in [a.getAction(self)['id']
            for a in self.controlpanel.listActions()]
        )

    def test_default_type_setting(self):
        self.assertTrue('default_type' in IMarkupSchema.names())
        self.assertEqual(
            self.settings.default_type,
            'text/html'
        )

    def test_allowed_types_setting(self):
        self.assertTrue('allowed_types' in IMarkupSchema.names())
        self.assertEqual(
            self.settings.allowed_types,
            ('text/html', 'text/x-web-textile')
        )
