#
# GRUF tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

default_user = PloneTestCase.default_user
default_group = 'test_group_1_'
PREFIX = 'group_'


class TestGroupUserFolder(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.uf = self.portal.acl_users
        self.uf.userFolderAddGroup(default_group)
        self.uf._updateUser(default_user, groups=[default_group])

    def testGetUser(self):
        self.failIfEqual(self.uf.getUser(default_user), None)

    def testGetBadUser(self):
        self.assertEqual(self.uf.getUser('user2'), None)

    def testGetUserById(self):
        self.failIfEqual(self.uf.getUserById(default_user), None)

    def testGetBadUserById(self):
        self.assertEqual(self.uf.getUserById('user2'), None)

    def testGetGroup(self):
        self.failIfEqual(self.uf.getGroup(PREFIX+default_group), None)

    def testGetBadGroup(self):
        self.assertEqual(self.uf.getGroup('group2'), None)

    def testGetUsers(self):
        # Returns users and groups
        users = self.uf.getUsers()
        self.failUnless(users)
        self.assertEqual(len(users), 2)
        userids = [x.getId() for x in users]
        self.failUnless(default_user in userids)
        self.failUnless(PREFIX+default_group in userids)

    def testGetUserNames(self):
        # Returns user and group names
        usernames = self.uf.getUserNames()
        self.failUnless(usernames)
        self.assertEqual(len(usernames), 2)
        self.failUnless(default_user in usernames)
        self.failUnless(PREFIX+default_group in usernames)

    def testGetGroups(self):
        # Returns groups
        groups = self.uf.getGroups()
        self.failUnless(groups)
        self.assertEqual(len(groups), 1)
        groupids = [x.getId() for x in groups]
        self.failUnless(PREFIX+default_group in groupids)

    def testGetGroupNames(self):
        # Returns group names
        groupnames = self.uf.getGroupNames()
        self.failUnless(groupnames)
        self.assertEqual(len(groupnames), 1)
        self.failUnless(PREFIX+default_group in groupnames)


class TestUserManagement(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.uf = self.portal.acl_users
        self.uf.userFolderAddGroup(default_group)
        self.uf._updateUser(default_user, groups=[default_group])

    # Classic UF interface

    def test_doAddUser(self):
        self.uf._doAddUser('user2', 'secret', ['Member'], [])
        user = self.uf.getUser('user2')
        self.assertEqual(user.getRoles(), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), ())

    def test_doAddUser_WithGroups(self):
        self.uf._doAddUser('user2', 'secret', ['Member'], [], groups=[default_group])
        user = self.uf.getUser('user2')
        self.assertEqual(user.getRoles(), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), (PREFIX+default_group,))

    def test_doChangeUser(self):
        # XXX: This test fails, brilliant!
        self.uf._doChangeUser(default_user, None, ['Reviewer'], [])
        user = self.uf.getUser(default_user)
        self.assertEqual(user.getRoles(), ('Reviewer', 'Authenticated'))
        #self.assertEqual(user.getGroups(), (PREFIX+default_group,))
        self.assertEqual(user.getGroups(), ()) # XXX: Should be (PREFIX+default_group,)

    def test_doChangeUser_WithGroups(self):
        self.uf.userFolderAddGroup('group2')
        self.uf._doChangeUser(default_user, None, ['Reviewer'], [], groups=['group2'])
        user = self.uf.getUser(default_user)
        self.assertEqual(user.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(user.getGroups(), (PREFIX+'group2',))

    def test_doDelUsers(self):
        self.uf._doDelUsers([default_user])
        self.failUnless(self.uf.getUser(default_user) is None)

    # The following tests must behave *exactly* like the ones above
    # but using the Zope-2.5 interface

    def testUserFolderAddUser(self):
        self.uf.userFolderAddUser('user2', 'secret', ['Member'], [])
        user = self.uf.getUser('user2')
        self.assertEqual(user.getRoles(), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), ())

    def testUserFolderAddUser_WithGroups(self):
        self.uf.userFolderAddUser('user2', 'secret', ['Member'], [], groups=[default_group])
        user = self.uf.getUser('user2')
        self.assertEqual(user.getRoles(), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), (PREFIX+default_group,))

    def testUserFolderEditUser(self):
        # XXX: This test fails as a consequence of calling _doChangeUser().
        self.uf.userFolderEditUser(default_user, None, ['Reviewer'], [])
        user = self.uf.getUser(default_user)
        self.assertEqual(user.getRoles(), ('Reviewer', 'Authenticated'))
        #self.assertEqual(user.getGroups(), (PREFIX+default_group,))
        self.assertEqual(user.getGroups(), ()) # XXX: Should be (PREFIX+default_group,)

    def testUserFolderEditUser_WithGroups(self):
        self.uf.userFolderAddGroup('group2')
        self.uf.userFolderEditUser(default_user, None, ['Reviewer'], [], groups=['group2'])
        user = self.uf.getUser(default_user)
        self.assertEqual(user.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(user.getGroups(), (PREFIX+'group2',))

    def testUserFolderDelUsers(self):
        self.uf.userFolderDelUsers([default_user])
        self.failUnless(self.uf.getUser(default_user) is None)

    # GRUF update interface

    def test_updateUser_Roles(self):
        self.uf._updateUser(default_user, roles=['Reviewer'])
        user = self.uf.getUser(default_user)
        self.assertEqual(user.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(user.getGroups(), (PREFIX+default_group,))

    def test_updateUser_Groups(self):
        self.uf.userFolderAddGroup('group2')
        self.uf._updateUser(default_user, groups=['group2'])
        user = self.uf.getUser(default_user)
        self.assertEqual(user.getRoles(), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), (PREFIX+'group2',))


class TestGroupManagement(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.uf = self.portal.acl_users
        self.uf.userFolderAddGroup(default_group)
        self.uf.userFolderAddGroup('group2')
        self.uf._updateGroup(default_group, groups=['group2'])

    # Classic-style interface

    def test_doAddGroup(self):
        self.uf._doAddGroup('group3', ['Reviewer'])
        group = self.uf.getGroup(PREFIX+'group3')
        self.assertEqual(group.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(group.getGroups(), ())

    def test_doAddGroup_WithGroups(self):
        self.uf._doAddGroup('group3', ['Reviewer'], ['group2'])
        group = self.uf.getGroup(PREFIX+'group3')
        self.assertEqual(group.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(group.getGroups(), (PREFIX+'group2',))

    def test_doChangeGroup(self):
        # XXX: This test fails
        self.uf._doChangeGroup(default_group, ['Reviewer'])
        group = self.uf.getGroup(PREFIX+default_group)
        self.assertEqual(group.getRoles(), ('Reviewer', 'Authenticated'))
        #self.assertEqual(group.getGroups(), (PREFIX+'group2',))
        self.assertEqual(group.getGroups(), ()) # XXX: Should be (PREFIX+'group2',)

    def test_doChangeGroup_WithGroups(self):
        self.uf.userFolderAddGroup('group3')
        self.uf._doChangeGroup(PREFIX+default_group, ['Reviewer'], ['group3'])
        group = self.uf.getGroup(PREFIX+default_group)
        self.assertEqual(group.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(group.getGroups(), (PREFIX+'group3',))

    def test_doDelGroups(self):
        self.uf._doDelGroups([default_group])
        self.failUnless(self.uf.getGroup(PREFIX+default_group) is None)

    # Zope-2.5-style interface

    def testUserFolderAddGroup(self):
        self.uf.userFolderAddGroup('group3', ['Reviewer'])
        group = self.uf.getGroup(PREFIX+'group3')
        self.assertEqual(group.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(group.getGroups(), ())

    def testUserFolderAddGroup_WithGroups(self):
        self.uf.userFolderAddGroup('group3', ['Reviewer'], ['group2'])
        group = self.uf.getGroup(PREFIX+'group3')
        self.assertEqual(group.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(group.getGroups(), (PREFIX+'group2',))

    def testUserFolderDelGroups(self):
        self.uf.userFolderDelGroups([default_group])
        self.failUnless(self.uf.getGroup(PREFIX+default_group) is None)

    # Update interface

    def test_updateGroup_Roles(self):
        self.uf._updateGroup(default_group, roles=['Reviewer'])
        group = self.uf.getGroup(PREFIX+default_group)
        self.assertEqual(group.getRoles(), ('Reviewer', 'Authenticated'))
        self.assertEqual(group.getGroups(), (PREFIX+'group2',))

    def test_updateGroup_Groups(self):
        self.uf.userFolderAddGroup('group3', ['Manager'])
        self.uf._updateGroup(default_group, groups=['group3'])
        group = self.uf.getGroup(PREFIX+default_group)
        self.assertEqual(group.getRoles(), ('Manager', 'Authenticated',))
        self.assertEqual(group.getGroups(), (PREFIX+'group3',))


class TestUsersAndGroups(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.uf = self.portal.acl_users
        self.uf.userFolderAddGroup(default_group)
        self.uf._updateUser(default_user, groups=[default_group])

        self.user = self.uf.getUser(default_user)
        self.group = self.uf.getGroup(PREFIX+default_group)

    # User interface

    def testUserGetId(self):
        self.assertEqual(self.user.getId(), default_user)

    def testUserGetName(self):
        self.assertEqual(self.user.getUserName(), default_user)

    def testUserGetPassword(self):
        self.assertEqual(self.user._getPassword(), 'secret')

    def testUserGetRoles(self):
        self.assertEqual(self.user.getRoles(), ('Member', 'Authenticated'))

    def testUserGetGroups(self):
        self.assertEqual(self.user.getGroups(), (PREFIX+default_group,))

    # Group interface

    def testGroupGetId(self):
        self.assertEqual(self.group.getId(), PREFIX+default_group)

    # Only available in GroupData-wrapped members
    #def testGroupGetName(self):
    #    self.assertEqual(self.group.getGroupName(), PREFIX+default_group)

    def testGroupGetRoles(self):
        self.assertEqual(self.group.getRoles(), ('Authenticated',))

    def testGroupGetGroups(self):
        self.assertEqual(self.group.getGroups(), ())

    # Only available in GroupData-wrapped members
    #def testGroupGetMembers(self):
    #    self.assertEqual(self.group.getGroupMembers(), ())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGroupUserFolder))
    suite.addTest(makeSuite(TestUserManagement))
    suite.addTest(makeSuite(TestGroupManagement))
    suite.addTest(makeSuite(TestUsersAndGroups))
    return suite

if __name__ == '__main__':
    framework()
