# Generic user folder tests. Every user folder implementation
# must pass these.

from AccessControl import Unauthorized
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.app.testing.bbb import _createMemberarea
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from ZPublisher.utils import basic_auth_encode

import unittest

user_role = 'Member'


class TestUserFolder(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        self.uf = self.portal.acl_users
        self.basic = basic_auth_encode(TEST_USER_NAME, TEST_USER_PASSWORD)

        _createMemberarea(self.portal, TEST_USER_ID)
        self.folder = self.portal.portal_membership.getHomeFolder(TEST_USER_ID)

        # Set up a published object accessible to the default user
        self.folder.addDTMLMethod('doc', file='')
        self.folder.doc.manage_permission('View', [user_role], acquire=0)
        # Rig the REQUEST so it looks like we traversed to 'doc'
        self.request.set('PUBLISHED', self.folder['doc'])
        self.request.set('PARENTS', [self.folder, self.portal])
        folder_path = list(self.folder.getPhysicalPath())
        self.request.steps = folder_path + ['doc']

        if 'auto_group' in self.uf:
            self.uf.manage_delObjects(['auto_group'])

        # Nuke Administators and Reviewers groups added in 2.1a2 migrations
        # (and any other migrated-in groups) to avoid test confusion
        self.portal.portal_groups.removeGroups(
            self.portal.portal_groups.listGroupIds())

        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, [user_role, ])

    def testGetUser(self):
        self.assertNotEqual(self.uf.getUser(TEST_USER_NAME), None)

    def testGetBadUser(self):
        self.assertEqual(self.uf.getUser('user2'), None)

    def testGetUserById(self):
        self.assertNotEqual(self.uf.getUserById(TEST_USER_ID), None)

    def testGetBadUserById(self):
        self.assertEqual(self.uf.getUserById('user2'), None)

    def testGetUsers(self):
        users = self.uf.getUsers()
        self.assertIn(
            TEST_USER_NAME,
            [u.getUserName() for u in users]
        )

    def testGetUserNames(self):
        names = self.uf.getUserNames()
        self.assertIn(
            TEST_USER_NAME,
            names
        )

    def testGetRoles(self):
        user = self.uf.getUser(TEST_USER_NAME)
        self.assertTrue(user_role in user.getRoles())

    def testGetRolesInContext(self):
        user = self.uf.getUser(TEST_USER_NAME)
        self.folder.manage_addLocalRoles(TEST_USER_ID, ['Owner'])
        roles = user.getRolesInContext(self.folder)
        self.assertTrue(user_role in roles)
        self.assertTrue('Owner' in roles)

    def testHasRole(self):
        user = self.uf.getUser(TEST_USER_NAME)
        self.assertTrue(user.has_role(user_role, self.folder))

    def testHasLocalRole(self):
        user = self.uf.getUser(TEST_USER_NAME)
        self.folder.manage_addLocalRoles(TEST_USER_ID, ['Owner'])
        self.assertTrue(user.has_role('Owner', self.folder))

    def testHasPermission(self):
        user = self.uf.getUser(TEST_USER_NAME)
        self.assertTrue(user.has_permission('View', self.folder))
        self.folder.manage_role(user_role, ['Add Folders'])
        self.assertTrue(user.has_permission('Add Folders', self.folder))

    def testHasLocalRolePermission(self):
        user = self.uf.getUser(TEST_USER_NAME)
        self.folder.manage_role('Owner', ['Add Folders'])
        self.folder.manage_addLocalRoles(TEST_USER_ID, ['Owner'])
        self.assertTrue(user.has_permission('Add Folders', self.folder))

    def testValidate(self):
        self.request._auth = self.basic
        user = self.uf.validate(self.request, self.basic, [user_role])
        self.assertNotEqual(user, None)
        self.assertEqual(user.getUserName(), TEST_USER_NAME)

    def testNotValidateWithoutAuth(self):
        self.request._auth = ''
        user = self.uf.validate(self.request, '', ['role1'])
        self.assertEqual(user, None)

    def testValidateWithoutRoles(self):
        self.request._auth = self.basic
        # Roles will be determined by looking at 'doc' itself
        user = self.uf.validate(self.request, self.basic)
        self.assertEqual(user.getUserName(), TEST_USER_NAME)

    def testNotValidateWithEmptyRoles(self):
        self.request._auth = self.basic
        user = self.uf.validate(self.request, self.basic, [])
        self.assertEqual(user, None)

    def testNotValidateWithWrongRoles(self):
        self.request._auth = self.basic
        user = self.uf.validate(self.request, self.basic, ['Manager'])
        self.assertEqual(user, None)

    def testAllowAccessToUser(self):
        login(self.portal, TEST_USER_NAME)
        try:
            self.folder.restrictedTraverse('doc')
        except Unauthorized:
            self.fail('Unauthorized')

    def testDenyAccessToAnonymous(self):
        logout()
        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, 'doc')
