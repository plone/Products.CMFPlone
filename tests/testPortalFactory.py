#
# Test portal factory
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from AccessControl.SecurityManagement import newSecurityManager

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestPortalFactory(PloneTestCase.PloneTestCase):

    def testTraverse(self):
        temp_doc = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.meta_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')

    def testTraverseTwiceByDifferentContentTypes(self):
        temp_doc = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.meta_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')
        temp_img = self.folder.restrictedTraverse('portal_factory/Image/tmp_id_image')
        self.assertEqual(temp_img.meta_type, 'Portal Image')
        self.assertEqual(temp_img.getId(), 'tmp_id_image')

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


    def testTempObjectLocalRoles(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('user2', 'secret', ['Member'], [])
        member = self.membership.getMemberById('user2')
        user = member.getUser()
        
        # assume identify of new user
        newSecurityManager(None, user)

        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        # make sure user is owner of temporary object
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object)),
                         ('Authenticated', 'Member', 'Owner'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalFactory))
    return suite

if __name__ == '__main__':
    framework()
