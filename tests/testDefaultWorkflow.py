#
# Tests the default workflow
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.WorkflowCore import WorkflowException
from AccessControl import Unauthorized

_user_name = ZopeTestCase._user_name


class TestDefaultWorkflow(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])

        #self.catalog.addColumn('allowedRolesAndUsers')
        self.folder.invokeFactory('Document', id='doc')

    def testOwnerHidesVisibleDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'visible')
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'private')
        self.failUnless(self.catalog(id='doc', review_state='private'))

    def testOwnerShowsPrivateDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'private')
        self.workflow.doActionFor(self.folder.doc, 'show')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    def testOwnerSubmitsVisibleDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'visible')
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'pending')
        self.failUnless(self.catalog(id='doc', review_state='pending'))

    def testOwnerHidesPendingDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'pending')
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'private')
        self.failUnless(self.catalog(id='doc', review_state='private'))

    def testOwnerRetractsPendingDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'pending')
        self.workflow.doActionFor(self.folder.doc, 'retract')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    def testOwnerRetractsPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'published')
        self.login(_user_name)
        self.workflow.doActionFor(self.folder.doc, 'retract')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    def testReviewerPublishesPendingDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'pending')
        self.login('reviewer')
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'published')
        self.failUnless(self.catalog(id='doc', review_state='published'))
        
    def testReviewerRejectsPendingDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'pending')
        self.login('reviewer')
        self.workflow.doActionFor(self.folder.doc, 'reject')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    def testReviewerPublishesVisibleDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'visible')
        self.login('reviewer')
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'published')
        self.failUnless(self.catalog(id='doc', review_state='published'))

    def testReviewerRejectsPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'published')
        self.workflow.doActionFor(self.folder.doc, 'reject')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    # Check some forbidden transitions

    def testOwnerSubmitsPrivateDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'private')
        self.assertRaises(WorkflowException, self.workflow.doActionFor, self.folder.doc, 'submit')

    def testManagerPublishesPrivateDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.folder.doc, 'review_state'), 'private')
        self.login('manager')
        self.assertRaises(WorkflowException, self.workflow.doActionFor, self.folder.doc, 'publish')

    # Check viewability

    def testViewVisibleDocument(self):
        # Owner is allowed
        self.folder.doc.restrictedTraverse('view')
        # Reviewer is allowed
        self.login('reviewer')
        self.folder.doc.restrictedTraverse('view')
        # Anonymous is allowed
        self.logout()
        self.folder.doc.restrictedTraverse('view')

    def testViewPrivateDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        # Owner is allowed
        self.folder.doc.restrictedTraverse('view')
        # Reviewer is denied
        self.login('reviewer')
        self.assertRaises(Unauthorized, self.folder.doc.restrictedTraverse, 'view')
        # Anonymous is denied
        self.logout()
        self.assertRaises(Unauthorized, self.folder.doc.restrictedTraverse, 'view')

    def testViewPendingDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        # Owner is allowed
        self.folder.doc.restrictedTraverse('view')
        # Reviewer is allowed
        self.login('reviewer')
        self.folder.doc.restrictedTraverse('view')
        # Anonymous is allowed (?)
        self.logout()
        #self.assertRaises(Unauthorized, self.folder.doc.restrictedTraverse, 'view')
        self.folder.doc.restrictedTraverse('view')

    def testViewPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.folder.doc, 'publish')
        # Owner is allowed
        self.login(_user_name)
        self.folder.doc.restrictedTraverse('view')
        # Reviewer is allowed
        self.login('reviewer')
        self.folder.doc.restrictedTraverse('view')
        # Anonymous is allowed
        self.logout()
        self.folder.doc.restrictedTraverse('view')

    # Check findability

    def testFindVisibleDocument(self):
        # Owner is allowed
        self.failUnless(self.catalog(id='doc'))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(self.catalog(id='doc'))
        # Anonymous is allowed (?)
        self.logout()
        self.failUnless(self.catalog(id='doc'))

    def testFindPrivateDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        # Owner is allowed
        self.failUnless(self.catalog(id='doc'))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(self.catalog(id='doc'))
        # Anonymous is denied
        self.logout()
        self.failIf(self.catalog(id='doc'))

    def testFindPendingDocument(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        # Owner is allowed
        self.failUnless(self.catalog(id='doc'))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(self.catalog(id='doc'))
        # Anonymous is allowed (?)
        self.logout()
        self.failUnless(self.catalog(id='doc'))

    def testFindPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.folder.doc, 'publish')
        # Owner is allowed
        self.login(_user_name)
        self.failUnless(self.catalog(id='doc'))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(self.catalog(id='doc'))
        # Anonymous is allowed
        self.logout()
        self.failUnless(self.catalog(id='doc'))


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestDefaultWorkflow))
        return suite

