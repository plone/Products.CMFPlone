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
        # Cannot assign a role I do not have myself...
        self.setRoles(['Member', 'Foo'])

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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFolderLocalRole))
    return suite

if __name__ == '__main__':
    framework()
