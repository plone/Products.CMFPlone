#
# Tests the default workflow
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.WorkflowCore import WorkflowException

from Products.CMFCore.utils import _checkPermission as checkPerm
from Products.CMFCore.CMFCorePermissions import AccessContentsInformation
from Products.CMFCore.CMFCorePermissions import View
from Products.CMFCore.CMFCorePermissions import ModifyPortalContent
from Products.CMFCalendar.EventPermissions import ChangeEvents

default_user = PloneTestCase.default_user


class TestDefaultWorkflow(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])

        self.folder.invokeFactory('Document', id='doc')
        self.doc = self.folder.doc

        self.folder.invokeFactory('Event', id='ev')
        self.ev = self.folder.ev

    # Check allowed transitions

    def testOwnerHidesVisibleDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.workflow.doActionFor(self.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        self.failUnless(self.catalog(id='doc', review_state='private'))

    def testOwnerShowsPrivateDocument(self):
        self.workflow.doActionFor(self.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        self.workflow.doActionFor(self.doc, 'show')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    def testOwnerSubmitsVisibleDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'pending')
        self.failUnless(self.catalog(id='doc', review_state='pending'))

    def testOwnerHidesPendingDocument(self):
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'pending')
        self.workflow.doActionFor(self.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        self.failUnless(self.catalog(id='doc', review_state='private'))

    def testOwnerRetractsPendingDocument(self):
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'pending')
        self.workflow.doActionFor(self.doc, 'retract')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    def testOwnerRetractsPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'published')
        self.login(default_user)
        self.workflow.doActionFor(self.doc, 'retract')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    def testReviewerPublishesPendingDocument(self):
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'pending')
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'published')
        self.failUnless(self.catalog(id='doc', review_state='published'))

    def testReviewerRejectsPendingDocument(self):
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'pending')
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'reject')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    def testReviewerPublishesVisibleDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'published')
        self.failUnless(self.catalog(id='doc', review_state='published'))

    def testReviewerRejectsPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'published')
        self.workflow.doActionFor(self.doc, 'reject')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.failUnless(self.catalog(id='doc', review_state='visible'))

    # Check some forbidden transitions

    def testOwnerPublishesVisibleDocument(self):
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'visible')
        self.assertRaises(WorkflowException, self.workflow.doActionFor, self.doc, 'publish')

    def testOwnerSubmitsPrivateDocument(self):
        self.workflow.doActionFor(self.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        self.assertRaises(WorkflowException, self.workflow.doActionFor, self.doc, 'submit')

    def testManagerPublishesPrivateDocument(self):
        self.workflow.doActionFor(self.doc, 'hide')
        self.assertEqual(self.workflow.getInfoFor(self.doc, 'review_state'), 'private')
        self.login('manager')
        self.assertRaises(WorkflowException, self.workflow.doActionFor, self.doc, 'publish')

    # No way am I going to write tests for all impossible transitions ;-)

    # Check view permission

    def testViewVisibleDocument(self):
        # Owner is allowed
        self.failUnless(checkPerm(View, self.doc))
        # Member is allowed
        self.login('member')
        self.failUnless(checkPerm(View, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(View, self.doc))
        # Anonymous is allowed
        self.logout()
        self.failUnless(checkPerm(View, self.doc))

    def testViewIsAcquiredInVisibleState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), 'CHECKED')

    def testViewPrivateDocument(self):
        self.workflow.doActionFor(self.doc, 'hide')
        # Owner is allowed
        self.failUnless(checkPerm(View, self.doc))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(View, self.doc))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(checkPerm(View, self.doc))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(View, self.doc))

    def testViewIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.doc, 'hide')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), '')

    def testViewPendingDocument(self):
        self.workflow.doActionFor(self.doc, 'submit')
        # Owner is allowed
        self.failUnless(checkPerm(View, self.doc))
        # Member is allowed (TODO:?)
        self.login('member')
        self.failUnless(checkPerm(View, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(View, self.doc))
        # Anonymous is allowed (TODO:?)
        self.logout()
        self.failUnless(checkPerm(View, self.doc))

    def testViewIsAcquiredInPendingState(self):
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), 'CHECKED')

    def testViewPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        # Owner is allowed
        self.login(default_user)
        self.failUnless(checkPerm(View, self.doc))
        # Member is allowed
        self.login('member')
        self.failUnless(checkPerm(View, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(View, self.doc))
        # Anonymous is allowed
        self.logout()
        self.failUnless(checkPerm(View, self.doc))

    def testViewIsAcquiredInPublishedState(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(View), 'CHECKED')

    # Check access contents info permission

    def testAccessVisibleDocument(self):
        # Owner is allowed
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Member is allowed
        self.login('member')
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is allowed
        self.logout()
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))

    def testAccessContentsInformationIsAcquiredInVisibleState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), 'CHECKED')

    def testAccessPrivateDocument(self):
        self.workflow.doActionFor(self.doc, 'hide')
        # Owner is allowed
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(AccessContentsInformation, self.doc))

    def testAccessContentsInformationIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.doc, 'hide')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), '')

    def testAccessPendingDocument(self):
        self.workflow.doActionFor(self.doc, 'submit')
        # Owner is allowed
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Member is allowed (TODO:?)
        self.login('member')
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is allowed (TODO:?)
        self.logout()
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))

    def testAccessContentsInformationIsAcquiredInPendingState(self):
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), 'CHECKED')

    def testAccessPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        # Owner is allowed
        self.login(default_user)
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Member is allowed
        self.login('member')
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))
        # Anonymous is allowed
        self.logout()
        self.failUnless(checkPerm(AccessContentsInformation, self.doc))

    def testAccessContentsInformationIsAcquiredInPublishedState(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(AccessContentsInformation), 'CHECKED')

    # Check modify content permissions

    def testModifyVisibleDocument(self):
        # Owner is allowed
        self.failUnless(checkPerm(ModifyPortalContent, self.doc))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(ModifyPortalContent, self.doc))

    def testModifyPortalContentIsNotAcquiredInVisibleState(self):
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), '')

    def testModifyPrivateDocument(self):
        self.workflow.doActionFor(self.doc, 'hide')
        # Owner is allowed
        self.failUnless(checkPerm(ModifyPortalContent, self.doc))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(ModifyPortalContent, self.doc))

    def testModifyPortalContentIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.doc, 'hide')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), '')

    def testModifyPendingDocument(self):
        self.workflow.doActionFor(self.doc, 'submit')
        # Owner is denied
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(ModifyPortalContent, self.doc))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(ModifyPortalContent, self.doc))

    def testModifyPortalContentIsNotAcquiredInPendingState(self):
        self.workflow.doActionFor(self.doc, 'submit')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), '')

    def testModifyPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        # Owner is denied
        self.login(default_user)
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(checkPerm(ModifyPortalContent, self.doc))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(ModifyPortalContent, self.doc))

    def testModifyPortalContentIsNotAcquiredInPublishedState(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        self.assertEqual(self.doc.acquiredRolesAreUsedBy(ModifyPortalContent), '')

    # Check change events permission

    def testModifyVisibleEvent(self):
        # Owner is allowed
        self.failUnless(checkPerm(ChangeEvents, self.ev))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(ChangeEvents, self.ev))

    def testChangeEventsIsNotAcquiredInVisibleState(self):
        self.assertEqual(self.ev.acquiredRolesAreUsedBy(ChangeEvents), '')

    def testModifyPrivateEvent(self):
        self.workflow.doActionFor(self.ev, 'hide')
        # Owner is allowed
        self.failUnless(checkPerm(ChangeEvents, self.ev))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(ChangeEvents, self.ev))

    def testChangeEventsIsNotAcquiredInPrivateState(self):
        self.workflow.doActionFor(self.ev, 'hide')
        self.assertEqual(self.ev.acquiredRolesAreUsedBy(ChangeEvents), '')

    def testModifyPendingEvent(self):
        self.workflow.doActionFor(self.ev, 'submit')
        # Owner is denied
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(checkPerm(ChangeEvents, self.ev))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(ChangeEvents, self.ev))

    def testChangeEventsIsNotAcquiredInPendingState(self):
        self.workflow.doActionFor(self.ev, 'submit')
        self.assertEqual(self.ev.acquiredRolesAreUsedBy(ChangeEvents), '')

    def testModifyPublishedEvent(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.ev, 'publish')
        # Owner is denied
        self.login(default_user)
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Member is denied
        self.login('member')
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(checkPerm(ChangeEvents, self.ev))
        # Anonymous is denied
        self.logout()
        self.failIf(checkPerm(ChangeEvents, self.ev))

    def testChangeEventsIsNotAcquiredInPublishedState(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.ev, 'publish')
        self.assertEqual(self.ev.acquiredRolesAreUsedBy(ChangeEvents), '')

    # Check catalog search

    def testFindVisibleDocument(self):
        # Owner is allowed
        self.failUnless(self.catalog(id='doc'))
        # Member is allowed
        self.login('member')
        self.failUnless(self.catalog(id='doc'))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(self.catalog(id='doc'))
        # Anonymous is allowed
        self.logout()
        self.failUnless(self.catalog(id='doc'))

    def testFindPrivateDocument(self):
        self.workflow.doActionFor(self.doc, 'hide')
        # Owner is allowed
        self.failUnless(self.catalog(id='doc'))
        # Member is denied
        self.login('member')
        self.failIf(self.catalog(id='doc'))
        # Reviewer is denied
        self.login('reviewer')
        self.failIf(self.catalog(id='doc'))
        # Anonymous is denied
        self.logout()
        self.failIf(self.catalog(id='doc'))

    def testFindPendingDocument(self):
        self.workflow.doActionFor(self.doc, 'submit')
        # Owner is allowed
        self.failUnless(self.catalog(id='doc'))
        # Member is allowed (TODO:?)
        self.login('member')
        self.failUnless(self.catalog(id='doc'))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(self.catalog(id='doc'))
        # Anonymous is allowed (TODO:?)
        self.logout()
        self.failUnless(self.catalog(id='doc'))

    def testFindPublishedDocument(self):
        self.login('reviewer')
        self.workflow.doActionFor(self.doc, 'publish')
        # Owner is allowed
        self.login(default_user)
        self.failUnless(self.catalog(id='doc'))
        # Member is allowed
        self.login('member')
        self.failUnless(self.catalog(id='doc'))
        # Reviewer is allowed
        self.login('reviewer')
        self.failUnless(self.catalog(id='doc'))
        # Anonymous is allowed
        self.logout()
        self.failUnless(self.catalog(id='doc'))

    def testMyWorklist(self):
        # When a member has the local Reviewer role, pending
        # docs should show up in his worklist.
        self.workflow.doActionFor(self.doc, 'submit')
        self.doc.manage_addLocalRoles('member', ['Reviewer'])
        self.login('reviewer')
        worklist = self.portal.my_worklist()
        self.failUnless(len(worklist) == 1)
        self.failUnless(worklist[0] == self.doc)
        self.login('member')
        worklist = self.portal.my_worklist()
        self.failUnless(len(worklist) == 1)
        self.failUnless(worklist[0] == self.doc)

    def testStateTitles(self):
        state_titles = { 'private': 'Private',
                        'visible': 'Public Draft',
                        'pending': 'Pending',
                        'published': 'Published'
                        }
        for wf in self.workflow.objectValues():
            for state_id, title in state_titles.items():
                state = getattr(wf.states, state_id, None)
                if state is not None:
                    self.assertEqual(state.title, title)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDefaultWorkflow))
    return suite

if __name__ == '__main__':
    framework()
