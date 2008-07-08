#
# GRUF3 tests
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.tests.base.testcase import WarningInterceptor

default_user = PloneTestCase.default_user
default_group = 'test_group_1_'
try:
    import Products.PlonePAS
except ImportError:
    PREFIX = 'group_'
else:
    PREFIX = ''


class TestGroupUserFolder(PloneTestCase.PloneTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.uf = self.portal.acl_users
        self._trap_warning_output()
        
        if 'auto_group' in self.uf.objectIds():
            self.uf.manage_delObjects(['auto_group'])

        # Nuke Administators and Reviewers groups added in 2.1a2 migrations
        # (and any other migrated-in groups) to avoid test confusion
        self.portal.portal_groups.removeGroups(self.portal.portal_groups.listGroupIds())
        
        self.uf.userFolderAddGroup(default_group, [])
        self.uf.userSetGroups(default_user, groupnames=[default_group])

    def testGetUser(self):
        self.failIfEqual(self.uf.getUser(default_user), None)

    def testGetBadUser(self):
        self.assertEqual(self.uf.getUser('user2'), None)

    def testGetUserById(self):
        self.failIfEqual(self.uf.getUserById(default_user), None)

    def testGetBadUserById(self):
        self.assertEqual(self.uf.getUserById('user2'), None)

    def testGetGroup(self):
        self.failIfEqual(self.uf.getGroup(default_group), None)

    def testGetBadGroup(self):
        self.assertEqual(self.uf.getGroup('group2'), None)

    def testGetGroupById(self):
        self.failIfEqual(self.uf.getGroupById(PREFIX+default_group), None)

    def testGetBadGroupById(self):
        self.assertEqual(self.uf.getGroupById('group2'), None)

    def testGetGroupByName(self):
        self.failIfEqual(self.uf.getGroupByName(default_group), None)

    def testGetBadGroupByName(self):
        self.assertEqual(self.uf.getGroupByName('group2'), None)

    def testGetUsers(self):
        # Returns users and groups
        users = self.uf.getUsers()
        self.failUnless(users)
        self.assertEqual(len(users), 1)
        userids = [x.getId() for x in users]
        self.failUnless(default_user in userids)
        self.failIf(PREFIX+default_group in userids)

    def testGetUserIds(self):
        # Returns user and group ids
        userids = self.uf.getUserIds()
        self.failUnless(userids)
        self.assertEqual(len(userids), 1)
        self.failUnless(default_user in userids)
        self.failIf(PREFIX+default_group in userids)

    def testGetUserNames(self):
        # Returns user and group names
        usernames = self.uf.getUserNames()
        self.failUnless(usernames)
        self.assertEqual(len(usernames), 1)
        self.failUnless(default_user in usernames)
        self.failIf(default_group in usernames)

    def testGetGroups(self):
        # Returns groups
        groups = self.uf.getGroups()
        self.failUnless(groups)
        self.assertEqual(len(groups), 1)
        groupids = [x.getId() for x in groups]
        self.failUnless(PREFIX+default_group in groupids)

    def testGetGroupIds(self):
        # Returns group ids
        groupids = self.uf.getGroupIds()
        self.failUnless(groupids)
        self.assertEqual(len(groupids), 1)
        self.failUnless(PREFIX+default_group in groupids)

    def testGetGroupNames(self):
        # Returns group names
        groupnames = self.uf.getGroupNames()
        self.failUnless(groupnames)
        self.assertEqual(len(groupnames), 1)
        self.failUnless(default_group in groupnames)

    def beforeTearDown(self):
        self._free_warning_output()


class TestUserManagement(PloneTestCase.PloneTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.uf = self.portal.acl_users
        self._trap_warning_output()

        if 'auto_group' in self.uf.objectIds():
            self.uf.manage_delObjects(['auto_group'])
        self.uf.userFolderAddGroup(default_group, [])
        self.uf.userSetGroups(default_user, groupnames=[default_group])

    # Classic UF interface

    def test_doAddUser(self):
        self.uf._doAddUser('user2', 'secret', ['Member'], [])
        user = self.uf.getUser('user2')
        self.assertEqual(tuple(user.getRoles()), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), [])  # XXX: Should be tuple
        self.assertEqual(user.getGroupIds(), [])
        self.assertEqual(user.getGroupNames(), [])

    def test_doAddUser_WithGroups(self):
        self.uf._doAddUser('user2', 'secret', ['Member'], [], [default_group])
        user = self.uf.getUser('user2')
        self.assertEqual(tuple(user.getRoles()), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), [PREFIX+default_group])  # XXX: WTF?
        self.assertEqual(user.getGroupIds(), [PREFIX+default_group])
        self.assertEqual(user.getGroupNames(), [default_group])

    def test_doChangeUser(self):
        self.uf._doChangeUser(default_user, None, ['Reviewer'], [])
        user = self.uf.getUser(default_user)
        self.assertEqual(tuple(user.getRoles()), ('Reviewer', 'Authenticated'))
        self.assertEqual(user.getGroups(), [PREFIX+default_group])

    def test_doChangeUser_WithGroups(self):
        self.uf.userFolderAddGroup('group2', [])
        self.uf._doChangeUser(default_user, None, ['Reviewer'], [], ['group2'])

        user = self.uf.getUser(default_user)
        self.assertEqual(tuple(user.getRoles()), ('Reviewer', 'Authenticated'))
        self.assertEqual(user.getGroups(), [PREFIX+'group2'])

    def test_doDelUsers(self):
        self.uf._doDelUsers([default_user])
        self.failUnless(self.uf.getUser(default_user) is None)

    # The following tests must behave *exactly* like the ones above
    # but using the Zope-2.5 interface

    def testUserFolderAddUser(self):
        self.uf.userFolderAddUser('user2', 'secret', ['Member'], [])
        user = self.uf.getUser('user2')
        self.assertEqual(tuple(user.getRoles()), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), [])
        self.assertEqual(user.getGroupIds(), [])
        self.assertEqual(user.getGroupNames(), [])

    def testUserFolderAddUser_WithGroups(self):
        self.uf.userFolderAddUser('user2', 'secret', ['Member'], [], [default_group])
        user = self.uf.getUser('user2')
        self.assertEqual(tuple(user.getRoles()), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), [PREFIX+default_group])
        self.assertEqual(user.getGroupIds(), [PREFIX+default_group])
        self.assertEqual(user.getGroupNames(), [default_group])

    def testUserFolderEditUser(self):
        self.uf.userFolderEditUser(default_user, None, ['Reviewer'], [])
        user = self.uf.getUser(default_user)
        self.assertEqual(tuple(user.getRoles()), ('Reviewer', 'Authenticated'))
        self.assertEqual(user.getGroups(), [PREFIX+default_group])

    def testUserFolderEditUser_WithGroups(self):
        self.uf.userFolderAddGroup('group2', [])
        self.uf.userFolderEditUser(default_user, None, ['Reviewer'], [], ['group2'])
        user = self.uf.getUser(default_user)
        self.assertEqual(tuple(user.getRoles()), ('Reviewer', 'Authenticated'))
        self.assertEqual(user.getGroups(), [PREFIX+'group2'])

    def testUserFolderDelUsers(self):
        self.uf.userFolderDelUsers([default_user])
        self.failUnless(self.uf.getUser(default_user) is None)

    # GRUF update interface

    def test_updateUser_Groups(self):
        self.uf.userFolderAddGroup('group2', [])
        self.uf.userSetGroups(default_user, groupnames=['group2'])
        user = self.uf.getUser(default_user)
        self.assertEqual(tuple(user.getRoles()), ('Member', 'Authenticated'))
        self.assertEqual(user.getGroups(), [PREFIX+'group2'])

    def beforeTearDown(self):
        self._free_warning_output()


class TestGroupManagement(PloneTestCase.PloneTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.uf = self.portal.acl_users
        self._trap_warning_output()

        if 'auto_group' in self.uf.objectIds():
            self.uf.manage_delObjects(['auto_group'])
        self.uf.userFolderAddGroup(default_group, [])
        self.uf.userFolderAddGroup('group2', [])

    # Classic-style interface

    def test_doAddGroup(self):
        self.uf._doAddGroup('group3', ['Reviewer'])
        group = self.uf.getGroup('group3')
        self.assertEqual(tuple(group.getRoles()), ('Reviewer', 'Authenticated'))
        self.assertEqual(group.getGroups(), [])  # XXX: Should be tuple

    def test_doChangeGroup(self):
        self.uf._doChangeGroup(default_group, ['Reviewer'])
        group = self.uf.getGroup(default_group)
        self.assertEqual(tuple(group.getRoles()), ('Reviewer', 'Authenticated'))

    def test_doDelGroups(self):
        self.uf._doDelGroups([default_group])
        self.failUnless(self.uf.getGroup(default_group) is None)

    # Zope-2.5-style interface

    def testUserFolderAddGroup(self):
        self.uf.userFolderAddGroup('group3', ['Reviewer'])
        group = self.uf.getGroup('group3')
        self.assertEqual(tuple(group.getRoles()), ('Reviewer', 'Authenticated'))
        self.assertEqual(group.getGroups(), [])

    def testUserFolderEditGroup(self):
        self.uf.userFolderEditGroup(default_group, ['Reviewer'], [])
        group = self.uf.getGroup(default_group)
        self.assertEqual(tuple(group.getRoles()), ('Reviewer', 'Authenticated'))

    def testUserFolderDelGroups(self):
        self.uf.userFolderDelGroups([default_group])
        self.failUnless(self.uf.getGroup(default_group) is None)

    # Update interface

    def test_updateGroup_Roles(self):
        self.uf._updateGroup(default_group, roles=['Reviewer'])
        group = self.uf.getGroup(default_group)
        self.assertEqual(tuple(group.getRoles()), ('Reviewer', 'Authenticated'))

    def beforeTearDown(self):
        self._free_warning_output()


class TestUsersAndGroups(PloneTestCase.PloneTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.uf = self.portal.acl_users
        self._trap_warning_output()

        self.uf.userFolderAddGroup(default_group, [])
        if 'auto_group' in self.uf.objectIds():
            self.uf.manage_delObjects(['auto_group'])
        self.uf.userSetGroups(default_user, groupnames=[default_group])

        self.user = self.uf.getUser(default_user)
        self.group = self.uf.getGroup(default_group)

    # User interface

    def testUserGetId(self):
        self.assertEqual(self.user.getId(), default_user)

    def testUserGetName(self):
        self.assertEqual(self.user.getUserName(), default_user)

    def testUserGetRoles(self):
        self.assertEqual(tuple(self.user.getRoles()), ('Member', 'Authenticated'))

    def testUserGetGroups(self):
        # XXX: This should return a tuple!
        # Also note that it returns group ids, i.e. including the prefix
        self.assertEqual(self.user.getGroups(), [PREFIX+default_group])

    def testUserGetGroupNames(self):
        self.assertEqual(self.user.getGroupNames(), [default_group]) # XXX: Should be tuple

    # Group interface

    def testGroupGetId(self):
        self.assertEqual(self.group.getId(), PREFIX+default_group)

    def testGroupGetName(self):
        # XXX: Bah! Why no getGroupName? Only available on GroupData-wrapped members!
        #self.assertEqual(self.group.getGroupName(), default_group)
        self.assertEqual(self.group.getName(), default_group)

    def testGroupGetRoles(self):
        self.assertEqual(tuple(self.group.getRoles()), ('Authenticated',))

    def testGroupGetGroups(self):
        self.assertEqual(self.group.getGroups(), []) # XXX: Should be tuple

    def testGroupGetGroupNames(self):
        self.assertEqual(self.group.getGroupNames(), []) # XXX: Should be tuple

    def testGroupGetMembers(self):
        # XXX: No getMembers! GroupData-wrapper provides getGroupMembers.
        pass

    def testGroupGetMemberIds(self):
        self.assertEqual(list(self.group.getMemberIds()), [default_user])

    def beforeTearDown(self):
        self._free_warning_output()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGroupUserFolder))
    suite.addTest(makeSuite(TestUserManagement))
    suite.addTest(makeSuite(TestGroupManagement))
    suite.addTest(makeSuite(TestUsersAndGroups))
    return suite
