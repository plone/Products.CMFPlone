from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import ISecuritySchema
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from zope.component import getAdapter

import unittest


class SecurityControlPanelEventsTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.security_settings = getAdapter(self.portal, ISecuritySchema)

    def _create_user(self, user_id=None, email=None):
        """Helper function for creating a test user."""
        registration = getToolByName(self.portal, 'portal_registration', None)
        registration.addMember(
            user_id,
            'password',
            ['Member'],
            properties={'email': email, 'username': user_id}
        )
        membership = getToolByName(self.portal, 'portal_membership', None)
        return membership.getMemberById(user_id)

    def _is_self_reg_enabled(self):
        """Helper function to determine if self registration was properly
        enabled.
        """
        app_perms = self.portal.rolesOfPermission(
            permission='Add portal member')
        for app_perm in app_perms:
            if app_perm['name'] == 'Anonymous' \
               and app_perm['selected'] == 'SELECTED':
                return True
        return False

    def test_handle_enable_self_reg_condition_check(self):
        """Check that this event handler is not run for other ISecuritySchema
        records.
        """
        self.assertFalse(self._is_self_reg_enabled())
        self.security_settings.use_uuid_as_userid = True
        self.assertFalse(self._is_self_reg_enabled())

    def test_handle_enable_self_reg_disabled(self):
        self.security_settings.enable_self_reg = False
        self.assertFalse(self._is_self_reg_enabled())

    def test_handle_enable_self_reg_enabled(self):
        self.security_settings.enable_self_reg = True
        self.assertTrue(self._is_self_reg_enabled())

    def test_handle_enable_user_folders_condition_check(self):
        """Check that this event handler is not run for other ISecuritySchema
        records.
        """
        portal_actions = getToolByName(self.portal, 'portal_actions', None)
        self.assertFalse('mystuff' in portal_actions['user'].keys())
        self.security_settings.use_uuid_as_userid = True
        self.assertFalse('mystuff' in portal_actions['user'].keys())

    def test_handle_enable_user_folders_enabled_no_mystuff_yet(self):
        portal_actions = getToolByName(self.portal, 'portal_actions', None)

        # if we enable the setting, mystuff action should be added
        self.assertFalse('mystuff' in portal_actions['user'].keys())
        self.security_settings.enable_user_folders = True
        self.assertTrue('mystuff' in portal_actions['user'].keys())
        self.assertTrue(portal_actions['user']['mystuff'].visible)

    def test_handle_enable_user_folders_enabled_has_mystuff(self):
        portal_actions = getToolByName(self.portal, 'portal_actions', None)

        # if we enable the setting, disable it, then enable it again,
        # the mystuff action should still be there and visible
        self.security_settings.enable_user_folders = True
        self.security_settings.enable_user_folders = False
        self.security_settings.enable_user_folders = True

        self.assertTrue('mystuff' in portal_actions['user'].keys())
        self.assertTrue(portal_actions['user']['mystuff'].visible)

    def test_handle_enable_user_folders_disabled_no_mystuff_yet(self):
        portal_actions = getToolByName(self.portal, 'portal_actions', None)

        # if the mystuff action is not there yet, this should have no effect
        self.security_settings.enable_user_folders = False
        self.assertFalse('mystuff' in portal_actions['user'].keys())

    def test_handle_enable_user_folders_disabled_has_mystuff(self):
        portal_actions = getToolByName(self.portal, 'portal_actions', None)

        # if the setting was enabled and then disabled, the mystuff action
        # should be hidden
        self.security_settings.enable_user_folders = True
        self.security_settings.enable_user_folders = False
        self.assertTrue('mystuff' in portal_actions['user'].keys())
        self.assertFalse(portal_actions['user']['mystuff'].visible)

    def test_handle_use_email_as_login_condition_check(self):
        """Check that this event handler is not run for other ISecuritySchema
        records.
        """
        self._create_user(user_id='joe', email='joe@test.com')
        pas = getToolByName(self.portal, 'acl_users')

        self.assertEqual(len(pas.searchUsers(name='joe@test.com')), 0)
        self.security_settings.use_uuid_as_userid = True
        self.assertEqual(len(pas.searchUsers(name='joe@test.com')), 0)

    def test_handle_use_email_as_login_enabled(self):
        self._create_user(user_id='joe', email='joe@test.com')
        pas = getToolByName(self.portal, 'acl_users')

        self.assertEqual(len(pas.searchUsers(name='joe@test.com')), 0)
        self.assertEqual(len(pas.searchUsers(name='joe')), 1)

        # if we enable use_email_as_login, login name should be migrated
        # to email
        self.security_settings.use_email_as_login = True
        self.assertEqual(len(pas.searchUsers(name='joe@test.com')), 1)

    def test_handle_use_email_as_login_disabled(self):
        self._create_user(user_id='joe', email='joe@test.com')
        pas = getToolByName(self.portal, 'acl_users')

        # if we enable use_email_as_login, then disabled it, the login name
        # should be migrated back to user id
        self.security_settings.use_email_as_login = True
        self.security_settings.use_email_as_login = False
        self.assertEqual(len(pas.searchUsers(name='joe@test.com')), 0)
        self.assertEqual(len(pas.searchUsers(name='joe')), 1)
