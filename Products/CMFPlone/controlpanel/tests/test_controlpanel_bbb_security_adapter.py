from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.CMFPlone.interfaces import ISecuritySchema
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.component import getAdapter

import unittest


class SecurityControlPanelAdapterTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.security_settings = getAdapter(self.portal, ISecuritySchema)

    def test_adapter_lookup(self):
        self.assertTrue(getAdapter(self.portal, ISecuritySchema))

    def test_get_enable_self_reg_setting(self):
        self.assertEqual(
            self.security_settings.enable_self_reg,
            False
        )

    def test_set_enable_self_reg_setting(self):
        self.security_settings.enable_self_reg = False
        self.assertEqual(
            self.security_settings.enable_self_reg,
            False
        )
        self.security_settings.enable_self_reg = True
        self.assertEqual(
            self.security_settings.enable_self_reg,
            True
        )

    def test_get_enable_user_pwd_choice_setting(self):
        self.assertEqual(
            self.security_settings.enable_user_pwd_choice,
            False
        )

    def test_set_enable_user_pwd_choice_setting(self):
        self.security_settings.enable_user_pwd_choice = False
        self.assertEqual(
            self.security_settings.enable_user_pwd_choice,
            False
        )
        self.security_settings.enable_user_pwd_choice = True
        self.assertEqual(
            self.security_settings.enable_user_pwd_choice,
            True
        )

    def test_get_enable_user_folders_setting(self):
        self.assertEqual(
            self.security_settings.enable_user_folders,
            False
        )

    def test_set_enable_user_folders_setting(self):
        self.security_settings.enable_user_folders = False
        self.assertEqual(
            self.security_settings.enable_user_folders,
            False
        )
        self.security_settings.enable_user_folders = True
        self.assertEqual(
            self.security_settings.enable_user_folders,
            True
        )

    def test_get_allow_anon_views_about_setting(self):
        self.assertEqual(
            self.security_settings.allow_anon_views_about,
            False
        )

    def test_set_allow_anon_views_about_setting(self):
        self.security_settings.allow_anon_views_about = False
        self.assertEqual(
            self.security_settings.allow_anon_views_about,
            False
        )
        self.security_settings.allow_anon_views_about = True
        self.assertEqual(
            self.security_settings.allow_anon_views_about,
            True
        )

    def test_get_use_email_as_login_setting(self):
        self.assertEqual(
            self.security_settings.use_email_as_login,
            False
        )

    def test_set_use_email_as_login_setting(self):
        self.security_settings.use_email_as_login = False
        self.assertEqual(
            self.security_settings.use_email_as_login,
            False
        )
        self.security_settings.use_email_as_login = True
        self.assertEqual(
            self.security_settings.use_email_as_login,
            True
        )

    def test_get_use_uuid_as_userid_setting(self):
        self.assertEqual(
            self.security_settings.use_uuid_as_userid,
            False
        )

    def test_set_use_uuid_as_userid_setting(self):
        self.security_settings.use_uuid_as_userid = False
        self.assertEqual(
            self.security_settings.use_uuid_as_userid,
            False
        )
        self.security_settings.use_uuid_as_userid = True
        self.assertEqual(
            self.security_settings.use_uuid_as_userid,
            True
        )
