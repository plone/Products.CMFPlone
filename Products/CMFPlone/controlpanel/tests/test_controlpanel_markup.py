# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IMarkupSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
import unittest2 as unittest


class MarkupRegistryIntegrationTest(unittest.TestCase):
    """Test plone.app.registry based markup storage.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IMarkupSchema, prefix="plone")

    def test_markup_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="markup-controlpanel")
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_markup_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('MarkupSettings' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()
        ])

    def test_default_type_exists(self):
        self.assertTrue(hasattr(self.settings, 'default_type'))

    def test_allowed_types_exists(self):
        self.assertTrue(hasattr(self.settings, 'allowed_types'))
