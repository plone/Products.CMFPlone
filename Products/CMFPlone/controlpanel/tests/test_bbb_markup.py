# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.testing.z2 import Browser
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IMarkupSchema

from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING


class EditingControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IMarkupSchema, prefix="plone")
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_default_type(self):
        self.browser.open(
            "%s/@@markup-controlpanel" % self.portal_url)
        self.browser.getControl('Default format').value = ['text/html']
        self.browser.getControl('Save').click()

        self.assertEqual(self.settings.default_type, 'text/html')

    def test_allowed_types(self):
        self.browser.open(
            "%s/@@markup-controlpanel" % self.portal_url)
        self.browser.getControl(
            name='form.widgets.allowed_types:list'
        ).value = ['text/plain', 'text/x-web-textile']
        self.browser.getControl('Save').click()

        self.assertEqual(
            self.settings.allowed_types,
            ('text/plain', 'text/x-web-textile'))