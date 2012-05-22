# Generic user folder tests. Every user folder implementation
# must pass these.

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.tests.base.testcase import WarningInterceptor

import base64
from AccessControl import Unauthorized

default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password
user_perms = ZopeTestCase.standard_permissions
user_role = 'Member'


class TestUserFolder(PloneTestCase.PloneTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.logout()
        self.uf = self.portal.acl_users
        self.basic = \
            'Basic %s' % base64.encodestring(
                            '%s:%s' % (default_user, default_password))
        # Set up a published object accessible to the default user
        self.folder.addDTMLMethod('doc', file='')
        self.folder.doc.manage_permission('View', [user_role], acquire=0)
        # Rig the REQUEST so it looks like we traversed to 'doc'
        self.app.REQUEST.set('PUBLISHED', self.folder['doc'])
        self.app.REQUEST.set('PARENTS', [self.folder, self.app])
        folder_path = list(self.folder.getPhysicalPath())
        self.app.REQUEST.steps = folder_path + ['doc']
        self._trap_warning_output()

        if 'auto_group' in self.uf:
            self.uf.manage_delObjects(['auto_group'])

        # Nuke Administators and Reviewers groups added in 2.1a2 migrations
        # (and any other migrated-in groups) to avoid test confusion
        self.portal.portal_groups.removeGroups(
            self.portal.portal_groups.listGroupIds())

    def testGetUser(self):
        self.assertNotEqual(self.uf.getUser(default_user), None)

    def testGetBadUser(self):
        self.assertEqual(self.uf.getUser('user2'), None)

    def testGetUserById(self):
        self.assertNotEqual(self.uf.getUserById(default_user), None)

    def testGetBadUserById(self):
        self.assertEqual(self.uf.getUserById('user2'), None)

    def testGetUsers(self):
        users = self.uf.getUsers()
        self.assertTrue(users)
        self.assertEqual(users[0].getUserName(), default_user)

    def testGetUserNames(self):
        names = self.uf.getUserNames()
        self.assertTrue(names)
        self.assertEqual(names[0], default_user)

    def testGetRoles(self):
        user = self.uf.getUser(default_user)
        self.assertTrue(user_role in user.getRoles())

    def testGetRolesInContext(self):
        user = self.uf.getUser(default_user)
        self.folder.manage_addLocalRoles(default_user, ['Owner'])
        roles = user.getRolesInContext(self.folder)
        self.assertTrue(user_role in roles)
        self.assertTrue('Owner' in roles)

    def testHasRole(self):
        user = self.uf.getUser(default_user)
        self.assertTrue(user.has_role(user_role, self.folder))

    def testHasLocalRole(self):
        user = self.uf.getUser(default_user)
        self.folder.manage_addLocalRoles(default_user, ['Owner'])
        self.assertTrue(user.has_role('Owner', self.folder))

    def testHasPermission(self):
        user = self.uf.getUser(default_user)
        self.assertTrue(user.has_permission('View', self.folder))
        self.folder.manage_role(user_role, ['Add Folders'])
        self.assertTrue(user.has_permission('Add Folders', self.folder))

    def testHasLocalRolePermission(self):
        user = self.uf.getUser(default_user)
        self.folder.manage_role('Owner', ['Add Folders'])
        self.folder.manage_addLocalRoles(default_user, ['Owner'])
        self.assertTrue(user.has_permission('Add Folders', self.folder))

    def testValidate(self):
        self.app.REQUEST._auth = self.basic
        user = self.uf.validate(self.app.REQUEST, self.basic, [user_role])
        self.assertNotEqual(user, None)
        self.assertEqual(user.getUserName(), default_user)

    def testNotValidateWithoutAuth(self):
        self.app.REQUEST._auth = ''
        user = self.uf.validate(self.app.REQUEST, '', ['role1'])
        self.assertEqual(user, None)

    def testValidateWithoutRoles(self):
        self.app.REQUEST._auth = self.basic
        # Roles will be determined by looking at 'doc' itself
        user = self.uf.validate(self.app.REQUEST, self.basic)
        self.assertEqual(user.getUserName(), default_user)

    def testNotValidateWithEmptyRoles(self):
        self.app.REQUEST._auth = self.basic
        user = self.uf.validate(self.app.REQUEST, self.basic, [])
        self.assertEqual(user, None)

    def testNotValidateWithWrongRoles(self):
        self.app.REQUEST._auth = self.basic
        user = self.uf.validate(self.app.REQUEST, self.basic, ['Manager'])
        self.assertEqual(user, None)

    def testAllowAccessToUser(self):
        self.login()
        try:
            self.folder.restrictedTraverse('doc')
        except Unauthorized:
            self.fail('Unauthorized')

    def testDenyAccessToAnonymous(self):
        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, 'doc')

    def beforeTearDown(self):
        self._free_warning_output()
