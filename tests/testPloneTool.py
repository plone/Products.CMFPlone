#
# Tests the PloneTool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

default_user = PloneTestCase.default_user


class TestPloneTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.membership = self.portal.portal_membership
        self.membership.addMember('new_owner', 'secret', ['Member'], [])

    def testChangeOwnershipOf(self):
        self.folder.invokeFactory('Document', 'doc')
        doc = self.folder.doc
        self.assertEqual(doc.Creator(), default_user)
        self.assertEqual(doc.get_local_roles_for_userid(default_user), ('Owner',))

        self.utils.changeOwnershipOf(doc, 'new_owner')
        self.assertEqual(doc.Creator(), 'new_owner')
        self.assertEqual(doc.get_local_roles_for_userid('new_owner'), ('Owner',))

        # Initial creator no longer has Owner role.
        self.assertEqual(doc.get_local_roles_for_userid(default_user), ())

    def testEditFormatMetadataOfFile(self):
        # Test workaround for http://plone.org/collector/1323
        # Also see setFormatPatch.py
        self.folder.invokeFactory('File', id='file')
        self.folder.file.edit(file=dummy.File('foo.zip'))
        self.assertEqual(self.folder.file.Format(), 'application/zip')
        self.assertEqual(self.folder.file.content_type, 'application/zip')
        # Changing the format should be reflected in content_type
        self.utils.editMetadata(self.folder.file, format='image/gif')
        self.assertEqual(self.folder.file.Format(), 'image/gif')
        self.assertEqual(self.folder.file.content_type, 'image/gif')

    def testEditFormatMetadataOfImage(self):
        # Test workaround for http://plone.org/collector/1323
        # Also see setFormatPatch.py
        self.folder.invokeFactory('Image', id='image')
        self.folder.image.edit(file=dummy.File('foo.zip'))
        self.assertEqual(self.folder.image.Format(), 'application/zip')
        self.assertEqual(self.folder.image.content_type, 'application/zip')
        # Changing the format should be reflected in content_type
        self.utils.editMetadata(self.folder.image, format='image/gif')
        self.assertEqual(self.folder.image.Format(), 'image/gif')
        self.assertEqual(self.folder.image.content_type, 'image/gif')

    def testEditFormatMetadataOfDocument(self):
        # Test workaround for http://plone.org/collector/1323
        # Also see setFormatPatch.py
        self.folder.invokeFactory('Document', id='doc',
                                  text_format='text/plain', text='foo')
        # Documents don't have a content_type property!
        self.failIf(self.folder.doc.hasProperty('content_type'))
        self.assertEqual(self.folder.doc.Format(), 'text/plain')
        self.assertEqual(self.folder.doc.content_type(), 'text/plain')
        # Changing the format should not create the property
        self.utils.editMetadata(self.folder.doc, format='text/html')
        self.failIf(self.folder.doc.hasProperty('content_type'))
        self.assertEqual(self.folder.doc.Format(), 'text/html')
        self.assertEqual(self.folder.doc.content_type(), 'text/html')


class TestExceptionsImport(ZopeTestCase.ZopeTestCase):
    '''We may be able to avoid raising 'Unauthorized' as string exception'''

    def afterSetUp(self):
        dispatcher = self.folder.manage_addProduct['PythonScripts']
        dispatcher.manage_addPythonScript('ps')
        self.ps = self.folder['ps']

    def testImportAccessControlUnauthorizedInPythonScript(self):
        # PythonScripts can import from AccessControl
        self.ps.ZPythonScript_edit('', 'from AccessControl import Unauthorized')
        self.ps()

    def testImportzExceptionsUnauthorizedInPythonScript(self):
        # PythonScripts can NOT import from zExceptions
        self.ps.ZPythonScript_edit('', 'from zExceptions import Unauthorized')
        self.assertRaises(ImportError, self.ps)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneTool))
    suite.addTest(makeSuite(TestExceptionsImport))
    return suite

if __name__ == '__main__':
    framework()
