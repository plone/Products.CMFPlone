#
# Test portal factory
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


class TestPortalFactory(PloneTestCase.PloneTestCase):

    def testTraverse(self):
        temp_doc = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.meta_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')

    def testTempFolderLocalRoles(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('user2', 'secret', ['Member'], [])
        self.portal._addRole('Foo')

        member = self.membership.getMemberById('user2')
        user = member.getUser()

        self.folder.manage_addLocalRoles('user2', ('Foo',))
        self.folder.invokeFactory(id='folder2', type_name='Folder')
        self.folder.folder2.manage_addLocalRoles('user2', ('Reviewer',))

        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))

        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object)),
                         ('Authenticated', 'Foo', 'Member'))

        temp_object2 = self.folder.folder2.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object2)),
                         ('Authenticated', 'Foo', 'Member', 'Reviewer'))


if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestPortalFactory))
        return suite
