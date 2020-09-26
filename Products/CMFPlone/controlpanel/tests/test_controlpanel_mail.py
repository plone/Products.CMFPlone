from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IMailSchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class MailRegistryIntegrationTest(unittest.TestCase):
    """Test that the mail settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IMailSchema, prefix="plone")

    def test_mail_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="mail-controlpanel")
        self.assertTrue(view())

    def test_mail_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue('MailHost' in [
            a.getAction(self)['id']
            for a in self.controlpanel.listActions()
        ])

    def test_mail_smtp_host_setting(self):
        self.assertTrue(hasattr(self.settings, 'smtp_host'))
