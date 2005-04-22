#
# Test check_id script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError

class TestFolderRename(PloneTestCase.PloneTestCase):
    # Tests for http://plone.org/collector/2876
    # folder_edit must recatalog. folder_rename must recatalog.

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Folder', id='foo')
        self.folder.invokeFactory('Folder', id='bar')
        self.folder.foo.invokeFactory('Document', id='doc1')
        self.folder.bar.invokeFactory('Document', id='doc2')

    def testTitleIsUpdatedOnTitleChange(self):
        # Make sure our title is updated on the object
        title = 'Test Doc - Snooze!'
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.folder.folder_rename(paths=[doc_path], new_ids=['doc1'], new_titles=[title])
        obj = self.folder.foo.doc1
        self.assertEqual(obj.Title(), title)

    def testCatalogTitleIsUpdatedOnFolderTitleChange(self):
        # Make sure our title is updated in the catalog
        title = 'Test Doc - Snooze!'
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.folder.folder_rename(paths=[doc_path], new_ids=['doc1'], new_titles=[title])
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'doc1')

    def testTitleAndIdAreUpdatedOnFolderRename(self):
        # Make sure rename updates both title and id
        title = 'Test Folder - Snooze!'
        get_transaction().commit(1) # make rename work
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.folder.folder_rename(paths=[doc_path], new_ids=['baz'], new_titles=[title])
        self.assertEqual(getattr(self.folder.foo, 'doc1', None), None)
        self.failUnless(getattr(self.folder.foo, 'baz', None) is not None)
        self.assertEqual(self.folder.foo.baz.Title(),title)

    def testCatalogTitleAndIdAreUpdatedOnFolderRename(self):
        # Make sure catalog updates title on rename
        title = 'Test Folder - Snooze!'
        get_transaction().commit(1) # make rename work
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.folder.folder_rename(paths=[doc_path], new_ids=['baz'], new_titles=[title])
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'baz')

    def testUpdateMultiplePaths(self):
        # Ensure this works for multiple paths
        title = 'Test Folder - Snooze!'
        get_transaction().commit(1) # make rename work
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        doc2_path = '/'.join(self.folder.bar.doc2.getPhysicalPath())
        self.folder.folder_rename(paths=[doc1_path,doc2_path], new_ids=['baz','blah'], new_titles=[title,title])
        self.assertEqual(getattr(self.folder.foo, 'doc1', None), None)
        self.assertEqual(getattr(self.folder.bar, 'doc2', None), None)
        self.failUnless(getattr(self.folder.foo, 'baz', None) is not None)
        self.failUnless(getattr(self.folder.bar, 'blah', None) is not None)
        self.assertEqual(self.folder.foo.baz.Title(),title)
        self.assertEqual(self.folder.bar.blah.Title(),title)

class TestFolderDelete(PloneTestCase.PloneTestCase):
    # Tests for http://plone.org/collector/2876
    # folder_edit must recatalog. folder_rename must recatalog.

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Folder', id='foo')
        self.folder.invokeFactory('Folder', id='bar')
        self.folder.foo.invokeFactory('Document', id='doc1')
        self.folder.bar.invokeFactory('Document', id='doc2')

    def testFolderDeletion(self):
        # Make sure object gets deleted
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.app.REQUEST.set('paths', [doc_path])
        self.folder.folder_delete()
        self.assertEqual(getattr(self.folder.foo, 'doc1', None), None)

    def testCatalogIsUpdatedOnFolderDelete(self):
        # Make sure catalog gets updated
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.app.REQUEST.set('paths', [doc_path])
        self.folder.folder_delete()
        results = self.catalog(path=doc_path)
        self.failIf(results)

    def testDeleteMultiplePaths(self):
        # Make sure deletion works for list of paths
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        doc2_path = '/'.join(self.folder.bar.doc2.getPhysicalPath())
        self.app.REQUEST.set('paths', [doc1_path,doc2_path])
        self.folder.folder_delete()
        self.assertEqual(getattr(self.folder.foo, 'doc1', None), None)
        self.assertEqual(getattr(self.folder.bar, 'doc2', None), None)

class TestFolderPublish(PloneTestCase.PloneTestCase):
    # Tests for http://plone.org/collector/2876
    # folder_edit must recatalog. folder_rename must recatalog.

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.wtool = self.portal.portal_workflow
        self.folder.invokeFactory('Folder', id='foo')
        self.folder.invokeFactory('Folder', id='bar')
        self.folder.foo.invokeFactory('Document', id='doc1')
        self.folder.bar.invokeFactory('Document', id='doc2')
        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])

    def testFolderPublishing(self):
        # Make sure object gets published
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.login('reviewer')
        self.folder.folder_publish(workflow_action='publish',paths=[doc_path])
        self.assertEqual(self.wtool.getInfoFor(self.folder.foo.doc1, 'review_state',None), 'published')

    def testCatalogIsUpdatedOnFolderPublish(self):
        # Make sure catalog gets updated
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.login('reviewer')
        self.folder.folder_publish(workflow_action='publish',paths=[doc_path])
        results = self.catalog(path=doc_path)
        self.assertEqual(len(results),1)
        self.assertEqual(results[0].review_state,'published')

    def testPublishMultiplePaths(self):
        # Make sure publish works for list of paths
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        doc2_path = '/'.join(self.folder.bar.doc2.getPhysicalPath())
        self.login('reviewer')
        self.folder.folder_publish('publish',paths=[doc1_path,doc2_path])
        self.assertEqual(self.wtool.getInfoFor(self.folder.foo.doc1, 'review_state',None), 'published')
        self.assertEqual(self.wtool.getInfoFor(self.folder.bar.doc2, 'review_state',None), 'published')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFolderRename))
    suite.addTest(makeSuite(TestFolderDelete))
    suite.addTest(makeSuite(TestFolderPublish))
    return suite

if __name__ == '__main__':
    framework()
