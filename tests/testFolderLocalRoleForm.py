#
# Tests folder local roles
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestFolderLocalRole(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('user2', 'secret', ['Member'], [])
        self.portal._addRole('Foo')
        self.portal._addRole('Bar')
        self.portal._addRole('FooBar')
        # Cannot assign a role I do not have myself...
        self.setRoles(['Member', 'Foo', 'Bar', 'FooBar'])

    def testFolderLocalRoleAdd(self):
        # Should assing a local role
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        member = self.membership.getMemberById('user2')
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))

    def testFolderLocalRoleDelete(self):
        # Should delete a local role
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        member = self.membership.getMemberById('user2')
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))
        self.folder.folder_localrole_edit('delete', ['user2'])
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Member'))

    def testFolderLocalRoleView(self):
        # Folder_localrole_form should render
        self.folder.folder_localrole_form()

    
    def testDeleteSingleRole(self):
        """try deleting a single role"""
        member = self.membership.getMemberById('user2')
        # add two roles
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        self.folder.folder_localrole_edit('add', ['user2'], 'Bar')

        # remove the Bar role
        self.folder.folder_localrole_delete(member_role_ids=['user2((Bar))',])
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))

    def testDeleteAllUserRoles(self):
        """try deleting a all roles"""
        member = self.membership.getMemberById('user2')
        # add two roles
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')
        self.folder.folder_localrole_edit('add', ['user2'], 'Bar')

        # remove a user
        self.folder.folder_localrole_delete(member_ids=['user2',])
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Member'))

    def testAddRoleForUser(self):
        """try adding a new role for a user"""
        member = self.membership.getMemberById('user2')
        # add a role the old way
        self.folder.folder_localrole_edit('add', ['user2'], 'Foo')

        # add another role the new way
        self.folder.folder_localrole_add(member_ids=['user2',],member_roles=['Bar','FooBar',])
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Bar', 'Foo', 'FooBar', 'Member'))

    def testIsLocalRoleAcquired(self):
        """ try setting the stop acquisition flag on a folder"""
        self.folder.acquireLocalRoles(status=0)
        self.assertEqual(self.folder.isLocalRoleAcquired(),0)

    def testStopAcquireLocalRole(self):
        """ See if a sub folder really didn't get the roles by acquisition"""
        member = self.membership.getMemberById('user2')
        self.folder.folder_localrole_add(member_ids=['user2',],member_roles=['Bar',])

        # check if the role was assigned
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Bar', 'Member'))

        self.folder.invokeFactory('Folder', id='A')
        self.folder.A.acquireLocalRoles(status=0)

        # check if inheritance is blocked
        self.assertEqual(sortTuple(member.getRolesInContext(self.folder.A)),
                         ('Authenticated', 'Member'))
        



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFolderLocalRole))
    return suite

if __name__ == '__main__':
    framework()
