#
# PloneFolder tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

try: from zExceptions import NotFound
except ImportError: NotFound = 'NotFound'


class TestPloneFolder(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # Create a bunch of subfolders
        self.folder.invokeFactory('Folder', id='sub1')
        self.folder.invokeFactory('Folder', id='sub2')
        self.folder.invokeFactory('Folder', id='sub3')

    def testGetObjectPosition(self):
        self.assertEqual(self.folder.getObjectPosition('.personal'), 0)

    def testGetObjectPositionRaisesNotFound(self):
        self.assertRaises(NotFound, self.folder.getObjectPosition, 'foobar')

    def testSortOrder(self):
        self.assertEqual(self.folder.objectIds(), 
            ['.personal', 'sub1', 'sub2', 'sub3'])

    def testEditFolderKeepsPosition(self):
        # Cover http://plone.org/collector/2796
        self.folder.sub2.folder_edit('Foo', 'Description')
        self.assertEqual(self.folder.sub2.Title(), 'Foo')
        # Order should remain the same
        self.assertEqual(self.folder.objectIds(), 
            ['.personal', 'sub1', 'sub2', 'sub3'])

    def testRenameFolderKeepsPosition(self):
        # Cover http://plone.org/collector/2796
        get_transaction().commit(1) # make rename work
        self.folder.sub2.folder_edit('Foo', 'Description', id='foo')
        self.assertEqual(self.folder.foo.Title(), 'Foo')
        # Order should remain the same
        self.assertEqual(self.folder.objectIds(), 
            ['.personal', 'sub1', 'foo', 'sub3'])


if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestPloneFolder))
        return suite
