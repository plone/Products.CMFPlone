#
# Tests for scripts behind folder_contents view
#

from cStringIO import StringIO
from zExceptions import Forbidden
from zope.interface import directlyProvides
from zope import component
from zope.container.interfaces import IObjectRemovedEvent
from Products.CMFPlone.tests import PloneTestCase
from Products.PloneTestCase.setup import default_user
from Products.PloneTestCase.setup import default_password
from Products.CMFPlone.tests.dummy import Item, ICantBeDeleted, \
                                          disallow_delete_handler
import transaction

PloneTestCase.installProduct('SiteAccess', quiet=1)


class TestFolderRename(PloneTestCase.PloneTestCase):
    # Tests for folder_rename and folder_rename_form

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Folder', id='foo')
        self.folder.invokeFactory('Folder', id='bar')
        self.folder.foo.invokeFactory('Document', id='doc1')
        self.folder.bar.invokeFactory('Document', id='doc2')
        # folder_rename requires a non-GET request
        self.setRequestMethod('POST')
        self.setupAuthenticator()

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
        transaction.savepoint(optimistic=True) # make rename work
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.folder.folder_rename(paths=[doc_path], new_ids=['baz'], new_titles=[title])
        self.assertEqual(getattr(self.folder.foo, 'doc1', None), None)
        self.failUnless(getattr(self.folder.foo, 'baz', None) is not None)
        self.assertEqual(self.folder.foo.baz.Title(),title)

    def testCatalogTitleAndIdAreUpdatedOnFolderRename(self):
        # Make sure catalog updates title on rename
        title = 'Test Folder - Snooze!'
        transaction.savepoint(optimistic=True) # make rename work
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
        transaction.savepoint(optimistic=True) # make rename work
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        doc2_path = '/'.join(self.folder.bar.doc2.getPhysicalPath())
        self.folder.folder_rename(paths=[doc1_path,doc2_path], new_ids=['baz','blah'], new_titles=[title,title])
        self.assertEqual(getattr(self.folder.foo, 'doc1', None), None)
        self.assertEqual(getattr(self.folder.bar, 'doc2', None), None)
        self.failUnless(getattr(self.folder.foo, 'baz', None) is not None)
        self.failUnless(getattr(self.folder.bar, 'blah', None) is not None)
        self.assertEqual(self.folder.foo.baz.Title(),title)
        self.assertEqual(self.folder.bar.blah.Title(),title)

    def testNoErrorOnBadPaths(self):
        # Ensure we don't fail on a bad path
        self.app.REQUEST.set('paths', ['/garbage/path'])
        self.folder.folder_rename_form()

    def testGETRaises(self):
        # folder_rename requires a non-GET request and will fail otherwise
        self.setRequestMethod('GET')
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.assertRaises(Forbidden, self.folder.folder_rename,
                          [doc1_path], ['bar'], ['Baz'])

    def testGetObjectsFromPathList(self):
        doc1_path = unicode('/'.join(self.folder.foo.doc1.getPhysicalPath()))
        doc2_path = unicode('/'.join(self.folder.bar.doc2.getPhysicalPath()))
        self.assertEqual(len(self.folder.getObjectsFromPathList([doc1_path, doc2_path])),2)


class TestFolderDelete(PloneTestCase.PloneTestCase):
    # Tests for folder_delete.py

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Folder', id='foo')
        self.folder.invokeFactory('Folder', id='bar')
        self.folder.foo.invokeFactory('Document', id='doc1')
        self.folder.bar.invokeFactory('Document', id='doc2')
        undeletable = Item('no_delete', 'Just Try!')
        # make it undeletable
        directlyProvides(undeletable, ICantBeDeleted)
        component.provideHandler(disallow_delete_handler, [ICantBeDeleted,
                                                           IObjectRemovedEvent])
        self.folder._setObject('no_delete', undeletable)
        # folder_delete requires a non-GET request
        self.setRequestMethod('POST')
        self.setupAuthenticator()

    def beforeTearDown(self):
        # unregister our deletion event subscriber
        component.getSiteManager().unregisterHandler(disallow_delete_handler,
                                                     [ICantBeDeleted,
                                                      IObjectRemovedEvent])

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

    def testNoErrorOnBadPaths(self):
        # Ensure we don't fail on a bad path
        self.app.REQUEST.set('paths', ['/garbage/path'])
        self.folder.folder_delete()

    def testObjectDeleteFailureIsCleanedUp(self):
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        doc2_path = '/'.join(self.folder.bar.doc2.getPhysicalPath())
        undeletable_path = '/'.join(self.folder.no_delete.getPhysicalPath())
        self.app.REQUEST.set('paths', [doc1_path, undeletable_path, doc2_path])
        self.folder.folder_delete()
        # The two deletable object should have been deleted
        self.assertEqual(getattr(self.folder.foo, 'doc1', None), None)
        self.assertEqual(getattr(self.folder.bar, 'doc2', None), None)
        # but the undeletable object will still be in place
        undeletable = getattr(self.folder, 'no_delete', None)
        self.failIfEqual(undeletable, None)
        # manage_beforeDelete will have been called, but the change it
        # makes should have been rolled back
        self.failIf(hasattr(undeletable, 'delete_attempted'))

    def testGETRaisesUnauthorized(self):
        # folder_delete requires a non-GET request and will fail otherwise
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.folder.folder_delete)



class TestFolderPublish(PloneTestCase.PloneTestCase):
    # Tests for folder_publish and content_status_history and
    # content_status_modify

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.wtool = self.portal.portal_workflow
        self.folder.invokeFactory('Folder', id='foo')
        self.folder.invokeFactory('Folder', id='bar')
        self.folder.foo.invokeFactory('Document', id='doc1')
        self.folder.bar.invokeFactory('Document', id='doc2')
        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])
        # folder_publish requires a non-GET request
        self.setRequestMethod('POST')

    def testFolderPublishing(self):
        # Make sure object gets published
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.login('reviewer')
        self.setupAuthenticator()
        self.folder.folder_publish(workflow_action='publish',paths=[doc_path])
        self.assertEqual(self.wtool.getInfoFor(self.folder.foo.doc1, 'review_state',None), 'published')

    def testCatalogIsUpdatedOnFolderPublish(self):
        # Make sure catalog gets updated
        doc_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.login('reviewer')
        self.setupAuthenticator()
        self.folder.folder_publish(workflow_action='publish',paths=[doc_path])
        results = self.catalog(path=doc_path)
        self.assertEqual(len(results),1)
        self.assertEqual(results[0].review_state,'published')

    def testPublishMultiplePaths(self):
        # Make sure publish works for list of paths
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        doc2_path = '/'.join(self.folder.bar.doc2.getPhysicalPath())
        self.login('reviewer')
        self.setupAuthenticator()
        self.folder.folder_publish('publish',paths=[doc1_path,doc2_path])
        self.assertEqual(self.wtool.getInfoFor(self.folder.foo.doc1, 'review_state',None), 'published')
        self.assertEqual(self.wtool.getInfoFor(self.folder.bar.doc2, 'review_state',None), 'published')

    def testNoErrorOnBadPaths(self):
        # Ensure we don't fail on a bad path, but transition the good ones
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        doc2_path = '/'.join(self.folder.bar.doc2.getPhysicalPath())
        paths=[doc1_path, '/garbage/path', doc2_path]
        self.login('reviewer')
        self.setupAuthenticator()
        self.folder.folder_publish('publish', paths=paths)
        self.assertEqual(self.wtool.getInfoFor(self.folder.foo.doc1,
                                               'review_state', None),
                         'published')
        self.assertEqual(self.wtool.getInfoFor(self.folder.bar.doc2,
                                               'review_state', None),
                         'published')

    def testPublishFailureIsCleanedUp(self):
        # Ensure we don't fail on a bad path, but transition the good ones

        # First we add a failing notifySuccess method to the workflow
        # via a nasty monkey-patch
        from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
        def notifySuccess(self, obj, action, result):
            raise Exception, 'Cannot transition'
        orig_notify = DCWorkflowDefinition.notifySuccess
        DCWorkflowDefinition.notifySuccess = notifySuccess

        # now we perform the transition
        doc1_path = '/'.join(self.folder.foo.doc1.getPhysicalPath())
        self.login('reviewer')
        self.setupAuthenticator()
        self.folder.folder_publish('publish', paths=[doc1_path])
        # because an error was raised during post transition the
        # transaction should have been rolled-back and the state
        # should not have changed
        self.failIfEqual(self.wtool.getInfoFor(self.folder.foo.doc1,
                                               'review_state', None),
                         'published')

        # undo our nasty patch
        DCWorkflowDefinition.notifySuccess = orig_notify

    def testGETRaises(self):
        # folder_rename requires a non-GET request and will fail otherwise
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.folder.folder_publish,
                          'publish', paths=['bogus'])


class TestFolderCutCopy(PloneTestCase.PloneTestCase):
    # Tests for folder_cut.py and folder_copy.py

    def testCutNoErrorOnBadPaths(self):
        # Ensure we don't fail on a bad path
        self.app.REQUEST.set('paths', ['/garbage/path'])
        self.folder.folder_cut()

    def testCopyNoErrorOnBadPaths(self):
        # Ensure we don't fail on a bad path
        self.app.REQUEST.set('paths', ['/garbage/path'])
        self.folder.folder_copy()


class TestObjectActions(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.basic_auth = '%s:%s' % (default_user, default_password)

    def assertStatusEqual(self, a, b, msg=''):
        if a != b:
            entries = self.portal.error_log.getLogEntries()
            if entries:
                msg = entries[0]['tb_text']
            else:
                if not msg:
                    msg = 'no error log entry available'
        self.failUnlessEqual(a, b, msg)

    def testObjectRenameWithoutVHM(self):
        self.folder.invokeFactory('Document', 'd1', title='Doc1')
        folderUrl = self.folder.absolute_url()
        objPath = '/'.join(self.folder.d1.getPhysicalPath())
        objectUrl = self.folder.d1.absolute_url()
        origTemplate = self.folder.d1.absolute_url() + '/document_view?foo=bar'

        response = self.publish(objPath + '/object_rename', self.basic_auth,
                                env={'HTTP_REFERER' : origTemplate})

        self.assertStatusEqual(response.getStatus(), 302) # Redirect to edit

        location = response.getHeader('Location').split('?')[0]
        params = {}
        for p in response.getHeader('Location').split('?')[1].split('&'):
            key, val = p.split('=')
            self.failIf(key in params)
            params[key] = val
        self.failUnless('paths%3Alist' in params)
        self.failUnless('orig_template' in params)

        self.failUnless(location.startswith(objectUrl), location)
        self.failUnless(location.endswith('folder_rename_form'), location)

        # Perform the redirect
        editFormPath = location[len(self.app.REQUEST.SERVER_URL):]
        newParams = "orig_template=%s" % params['orig_template']
        newParams += "&paths:list=%s" % params['paths%3Alist']
        response = self.publish("%s?%s" % (editFormPath, newParams,), self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200)

        # Set up next set of params, faking user submission
        newParams += "&form.submitted=1"
        newParams += "&form.button.renameAll=Rename All"
        newParams += "&new_ids:list=%s" % 'new-id'
        newParams += "&new_titles:list=%s" % 'New title'
        newParams += '&%s=%s' % self.getAuthenticator()

        data = StringIO(newParams)
        response = self.publish(editFormPath, self.basic_auth,
                                request_method='POST', stdin=data)
        self.assertStatusEqual(response.getStatus(), 302)

        # Make sure we landed in the right place
        location = response.getHeader('Location').split('?')[0]
        self.failUnless(location.startswith(folderUrl + '/new-id'), location)
        self.failUnless(location.endswith('document_view'), location)

        self.failUnless('new-id' in self.folder)
        self.failIf('d1' in self.folder)
        self.assertEqual(self.folder['new-id'].Title(), 'New title')

    def testObjectRenameWithVHM(self):
        adding = self.app.manage_addProduct['SiteAccess']
        adding.manage_addVirtualHostMonster('vhm')

        vhmBasePath = "/VirtualHostBase/http/example.org:80/%s/VirtualHostRoot/" % self.portal.getId()
        vhmBaseUrl = 'http://example.org/'

        self.folder.invokeFactory('Document', 'd1', title='Doc1')
        folderPath = vhmBasePath + '/'.join(self.folder.getPhysicalPath()[2:])
        folderUrl = vhmBaseUrl + '/'.join(self.folder.getPhysicalPath()[2:])
        objPath = vhmBasePath + '/'.join(self.folder.d1.getPhysicalPath()[2:])
        objectUrl = vhmBaseUrl + '/'.join(self.folder.d1.getPhysicalPath()[2:])

        origTemplate = objectUrl + '/document_view?foo=bar'

        response = self.publish(objPath + '/object_rename', self.basic_auth,
                                env={'HTTP_REFERER' : origTemplate})

        self.assertStatusEqual(response.getStatus(), 302) # Redirect to edit

        location = response.getHeader('Location').split('?')[0]
        params = {}
        for p in response.getHeader('Location').split('?')[1].split('&'):
            key, val = p.split('=')
            self.failIf(key in params)
            params[key] = val
        self.failUnless('paths%3Alist' in params)
        self.failUnless('orig_template' in params)

        self.failUnless(location.startswith(objectUrl), location)
        self.failUnless(location.endswith('folder_rename_form'), location)

        # Perform the redirect
        editFormPath = vhmBasePath + location[len(vhmBaseUrl):]
        newParams = "orig_template=%s" % params['orig_template']
        newParams += "&paths:list=%s" % params['paths%3Alist']
        response = self.publish("%s?%s" % (editFormPath, newParams,), self.basic_auth)
        self.assertStatusEqual(response.getStatus(), 200)

        # Set up next set of params, faking user submission
        newParams += "&form.submitted=1"
        newParams += "&form.button.renameAll=Rename All"
        newParams += "&new_ids:list=%s" % 'new-id'
        newParams += "&new_titles:list=%s" % 'New title'
        newParams += '&%s=%s' % self.getAuthenticator()

        data = StringIO(newParams)
        response = self.publish(editFormPath, self.basic_auth,
                                request_method='POST', stdin=data)
        self.assertStatusEqual(response.getStatus(), 302)

        # Make sure we landed in the right place
        location = response.getHeader('Location').split('?')[0]
        self.failUnless(location.startswith(folderUrl + '/new-id'), location)
        self.failUnless(location.endswith('document_view'), location)

        self.failUnless('new-id' in self.folder)
        self.failIf('d1' in self.folder)
        self.assertEqual(self.folder['new-id'].Title(), 'New title')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFolderRename))
    suite.addTest(makeSuite(TestFolderDelete))
    suite.addTest(makeSuite(TestFolderPublish))
    suite.addTest(makeSuite(TestFolderCutCopy))
    suite.addTest(makeSuite(TestObjectActions))
    return suite
