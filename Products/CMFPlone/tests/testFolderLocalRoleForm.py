#
# Tests folder local roles
#

from Products.CMFPlone.tests import PloneTestCase
from zExceptions import Forbidden

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestFolderLocalRole(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('user2', 'secret', ['Member'], [])
        self.portal.acl_users.addRole('Foo')
        self.portal.acl_users.addRole('Bar')
        self.portal.acl_users.addRole('Baz')
        # Cannot assign a role I do not have myself...
        self.setRoles(['Member', 'Foo', 'Bar', 'Baz'])
        self.setupAuthenticator()

    def testFolderLocalRoleAddPostOnly(self):
        # Should try to use get on assing a local role
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.folder.folder_localrole_edit,'add',['user2'],'Foo')

    def testFolderLocalRoleDeletePostOnly(self):
        # Should try to use get on delete a local role
        self.setRequestMethod('POST')
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.folder.folder_localrole_edit,'delete',['user2'])

    def testFolderLocalRoleDelete2PostOnly(self):
        # Should try to use get on delete a local role
        self.setRequestMethod('POST')
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.folder.folder_localrole_delete,['user2'])

    def testFolderLocalRoleSetPostOnly(self):
        # Should try to use get on assing a local role
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.folder.folder_localrole_set)

    def testFolderLocalRoleAdd(self):
        # Should assing a local role
        self.setRequestMethod('POST')
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        self.setRequestMethod('GET')
        member = self.membership.getMemberById('user2')
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))

    def testFolderLocalRoleDelete(self):
        # Should delete a local role
        self.setRequestMethod('POST')
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        member = self.membership.getMemberById('user2')
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))
        self.folder.folder_localrole_edit('delete', ['user2'])
        self.setRequestMethod('GET')
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Member'))

    def testFolderLocalRoleView(self):
        # sharing should render
        self.loginAsPortalOwner()
        view = self.folder.restrictedTraverse("sharing")
        view()

    def testDeleteSingleRole(self):
        # Try deleting a single role
        member = self.membership.getMemberById('user2')
        # add two roles
        self.setRequestMethod('POST')
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        self.folder.folder_localrole_edit('add', ['user2'], 'Bar')

        # remove the Bar role
        self.folder.folder_localrole_delete(member_role_ids=['user2((Bar))'])
        self.setRequestMethod('GET')
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))

    def testDeleteAllUserRoles(self):
        # Try deleting a all roles
        member = self.membership.getMemberById('user2')
        # add two roles
        self.setRequestMethod('POST')
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        self.folder.folder_localrole_edit('add', ['user2'], 'Bar')

        # remove a user
        self.folder.folder_localrole_delete(member_ids=['user2'])
        self.setRequestMethod('GET')
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Member'))

    def testAddRoleForUser(self):
        # Try adding a new role for a user
        member = self.membership.getMemberById('user2')
        # add a role the old way
        self.setRequestMethod('POST')
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')

        # add another role the new way
        self.folder.folder_localrole_add(member_ids=['user2'], member_roles=['Bar', 'Baz'])
        self.setRequestMethod('GET')
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Bar', 'Baz', 'Foo', 'Member'))

    def testIsLocalRoleAcquired(self):
        # Try setting the stop acquisition flag on a folder
        putils = self.portal.plone_utils
        putils.acquireLocalRoles(self.folder, status=0)
        self.assertEqual(putils.isLocalRoleAcquired(self.folder), 0)

    def testStopAcquireLocalRole(self):
        # See if a sub folder really didn't get the roles by acquisition
        member = self.membership.getMemberById('user2')
        self.setRequestMethod('POST')
        self.folder.folder_localrole_add(member_ids=['user2'], member_roles=['Bar'])

        # check if the role was assigned
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Bar', 'Member'))

        self.folder.invokeFactory('Folder', id='A')
        putils = self.portal.plone_utils
        putils.acquireLocalRoles(self.folder.A, status=0)
        self.setRequestMethod('GET')

        # check if inheritance is blocked
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder.A)),
                         ('Authenticated', 'Member'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFolderLocalRole))
    return suite
