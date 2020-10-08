from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, setRoles
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest


class SecurityRegistryIntegrationTest(unittest.TestCase):
    """Test that the security settings are stored as plone.app.registry
    settings.
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ISecuritySchema, prefix="plone")

    def test_security_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="security-controlpanel")
        self.assertTrue(view())

    def test_plone_app_registry_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertTrue(
            'plone.app.registry' in [
                a.getAction(self)['id']
                for a in self.controlpanel.listActions()])

    def test_enable_self_reg_setting(self):
        self.assertTrue(hasattr(self.settings, 'enable_self_reg'))

    def test_enable_user_pwd_choice_setting(self):
        self.assertTrue(hasattr(self.settings, 'enable_user_pwd_choice'))

    def test_enable_user_folders_setting(self):
        self.assertTrue(hasattr(self.settings, 'enable_user_folders'))

    def test_allow_anon_views_about_setting(self):
        self.assertTrue(hasattr(self.settings, 'allow_anon_views_about'))

    def test_use_email_as_login_setting(self):
        self.assertTrue(hasattr(self.settings, 'use_email_as_login'))

    def test_use_uuid_as_userid_setting(self):
        self.assertTrue(hasattr(self.settings, 'use_uuid_as_userid'))
