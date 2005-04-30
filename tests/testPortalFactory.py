#
# Test portal factory
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from AccessControl import Unauthorized
default_user = PloneTestCase.default_user

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestPortalFactory(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('member', 'secret', ['Member'], [])
        self.membership.addMember('manager', 'secret', ['Manager'], [])

    def testTraverse(self):
        temp_doc = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.portal_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')

    def testTraverseTwiceByDifferentContentTypes(self):
        temp_doc = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(temp_doc.portal_type, 'Document')
        self.assertEqual(temp_doc.getId(), 'tmp_id')
        temp_img = self.folder.restrictedTraverse('portal_factory/Image/tmp_id_image')
        self.assertEqual(temp_img.portal_type, 'Image')
        self.assertEqual(temp_img.getId(), 'tmp_id_image')

    def testTempFolderLocalRoles(self):
        # Temporary objects should "inherit" local roles from container
        member = self.membership.getMemberById('member')
        self.portal._addRole('Foo')

        self.folder.manage_addLocalRoles('member', ('Foo',))
        self.folder.invokeFactory('Folder', id='folder2')
        self.folder.folder2.manage_addLocalRoles('member', ('Reviewer',))

        self.assertEqual(sortTuple(member.getRolesInContext(self.folder)),
                         ('Authenticated', 'Foo', 'Member'))

        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object)),
                         ('Authenticated', 'Foo', 'Member'))

        temp_object2 = self.folder.folder2.restrictedTraverse('portal_factory/Document/tmp_id')
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object2)),
                         ('Authenticated', 'Foo', 'Member', 'Reviewer'))

    def testTempObjectLocalRolesBug(self):
        # Evil monkey patch should not change all objects of a class
        self.createMemberarea('member')
        member = self.membership.getMemberById('member')

        # Make an unrelated non-temporary object for comparison
        self.login('manager')
        self.portal.invokeFactory('Document', id='nontmp_id')
        nontemp_object = getattr(self.portal, 'nontmp_id')

        # Assume identify of the ordinary member
        self.login('member')
        folder = self.membership.getHomeFolder()
        temp_object = folder.restrictedTraverse('portal_factory/Document/tmp_id')

        # Make sure member is owner of temporary object
        self.assertEqual(sortTuple(member.getRolesInContext(temp_object)),
                         ('Authenticated', 'Member', 'Owner'))
        self.assertEqual(temp_object.Creator(), 'member')

        # Make sure member is not owner of non-temporary object
        # (i.e. make sure our evil monkey patch of the temporary instance has
        # not resulted in our patching all instances of the class)
        self.assertEqual(sortTuple(member.getRolesInContext(nontemp_object)),
                         ('Authenticated', 'Member'))

    def testTempFolderPermissions(self):
        # TempFolder should "inherit" permission mappings from container
        from Products.CMFCore.CMFCorePermissions import AddPortalContent

        previous_roles = self.folder.rolesOfPermission(AddPortalContent)
        self.folder.manage_permission(AddPortalContent, ['Anonymous'], 1)
        new_roles = self.folder.rolesOfPermission(AddPortalContent)
        self.failIfEqual(previous_roles, new_roles)

        temp_folder = self.folder.restrictedTraverse(
                                'portal_factory/Document/tmp_id').aq_parent
        temp_roles = temp_folder.rolesOfPermission(AddPortalContent)
        self.assertEqual(temp_roles, new_roles)


class TestCreateObject(PloneTestCase.PloneTestCase):

    def testCreateObjectByDoCreate(self):
        # doCreate should create the real object
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        foo = temp_object.portal_factory.doCreate(temp_object, 'foo')
        self.failUnless('foo' in self.folder.objectIds())
        self.assertEqual(foo.get_local_roles_for_userid(default_user), ('Owner',))

    def testUnauthorizedToCreateObjectByDoCreate(self):
        # Anonymous should not be able to create the (real) object
        # Note that Anonymous used to be able to create the temp object...
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.logout()
        self.assertRaises(Unauthorized, temp_object.portal_factory.doCreate,
                          temp_object, 'foo')

    def testCreateObjectByDocumentEdit(self):
        # document_edit should create the real object
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        temp_object.document_edit(id='foo', title='Foo', text_format='plain', text='')
        self.failUnless('foo' in self.folder.objectIds())
        self.assertEqual(self.folder.foo.Title(), 'Foo')
        self.assertEqual(self.folder.foo.get_local_roles_for_userid(default_user), ('Owner',))

    def testUnauthorizedToCreateObjectByDocumentEdit(self):
        # Anonymous should not be able to create the (real) object
        # Note that Anonymous used to be able to create the temp object...
        temp_object = self.folder.restrictedTraverse('portal_factory/Document/tmp_id')
        self.logout()
        self.assertRaises(Unauthorized, temp_object.document_edit,
                          id='foo', title='Foo', text_format='plain', text='')


class TestCreateObjectByURL(PloneTestCase.FunctionalTestCase):
    '''Weeee, functional tests'''

    def afterSetUp(self):
        self.folder_url = self.folder.absolute_url()
        self.folder_path = '/%s' % self.folder.absolute_url(1)
        self.basic_auth = '%s:secret' % default_user
        # We want 401 responses, not redirects to a login page
        self.portal._delObject('cookie_authentication')
        # Enable portal_factory for Document type
        self.factory = self.portal.portal_factory
        self.factory.manage_setPortalFactoryTypes(listOfTypeIds=['Document'])

    def testCreateObject(self):
        # createObject script should make a temp object
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                self.basic_auth)

        self.assertEqual(response.getStatus(), 302) # Redirect to document_edit_form

        # The redirect URL should contain the factory parts
        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.folder_url+'/portal_factory/Document/'))
        self.failUnless(location.endswith('/atct_edit'))

        # Perform the redirect
        edit_form_path = location[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

    def testCreateNonGloballyAllowedObject(self):
        # TempFolder allows to create all portal types
        self.portal.portal_types.Document.manage_changeProperties(global_allow=0)
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                self.basic_auth)

        self.assertEqual(response.getStatus(), 302) # Redirect to document_edit_form

        # The redirect URL should contain the factory parts
        location = response.getHeader('Location')
        self.failUnless(location.startswith(self.folder_url+'/portal_factory/Document/'))
        self.failUnless(location.endswith('/atct_edit'))

        # Perform the redirect
        edit_form_path = location[len(self.app.REQUEST.SERVER_URL):]
        response = self.publish(edit_form_path, self.basic_auth)
        self.assertEqual(response.getStatus(), 200) # OK

    def testUnauthorizedToViewEditForm(self):
        # Anonymous should not be able to see document_edit_form
        response = self.publish(self.folder_path +
                                '/createObject?type_name=Document',
                                ) # No basic out info

        self.assertEqual(response.getStatus(), 401) # Unauthorized

    def testUnauthorizedToViewEditFormOfNonFactoryObject(self):
        # Anonymous should not be able to see newsitem_edit_form
        response = self.publish(self.folder_path +
                                '/createObject?type_name=News%20Item',
                                ) # No basic out info

        self.assertEqual(response.getStatus(), 401) # Unauthorized

    def testCreateObjectByDocumentEdit(self):
        # document_edit should create the real object
        response = self.publish(self.folder_path +
            '/portal_factory/Document/tmp_id/document_edit?id=foo&title=Foo&text_format=plain&text=',
            self.basic_auth)

        self.assertEqual(response.getStatus(), 302) # Redirect to document_view
        self.failUnless(response.getHeader('Location').startswith(self.folder_url+'/foo/view'))

        self.failUnless('foo' in self.folder.objectIds())
        self.assertEqual(self.folder.foo.Title(), 'Foo')
        self.assertEqual(self.folder.foo.get_local_roles_for_userid(default_user), ('Owner',))

    def testUnauthorizedToCreateObjectByDocumentEdit(self):
        # Anonymous should not be able to create the real object
        response = self.publish(self.folder_path +
            '/portal_factory/Document/tmp_id/document_edit?id=foo&title=Foo&text_format=plain&text=',
            ) # No basic auth info

        self.assertEqual(response.getStatus(), 401) # Unauthorized


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortalFactory))
    suite.addTest(makeSuite(TestCreateObject))
    suite.addTest(makeSuite(TestCreateObjectByURL))
    return suite

if __name__ == '__main__':
    framework()
