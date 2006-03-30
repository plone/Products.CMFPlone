#
# Tests the workflow tool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

default_user = PloneTestCase.default_user


class TestWorkflowTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.workflow = self.portal.portal_workflow

        self.portal.acl_users._doAddUser('member', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('reviewer', 'secret', ['Reviewer'], [])
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])

        self.folder.invokeFactory('Document', id='doc')
        self.doc = self.folder.doc

        self.folder.invokeFactory('Event', id='ev')
        self.ev = self.folder.ev

    def testGetTransitionsForProvidesURL(self):
        trans = self.workflow.getTransitionsFor(self.doc)
        self.assertEqual(len(trans), 2)
        self.failUnless(trans[0].has_key('url'))
        # Test that url has filled in string substitutions for content url
        self.failUnless('http://' in trans[0]['url'])

    def testGetTitleForStateOnType(self):
        state_id = self.workflow.getInfoFor(self.doc, 'review_state', '')
        state_title = self.workflow.getTitleForStateOnType(state_id, self.doc.portal_type)
        self.assertEqual(state_id, 'visible')
        self.assertEqual(state_title, 'Public Draft')

    def testGetTitleForStateOnTypeFallsBackOnStateId(self):
        state_id = 'nonsense'
        state_title = self.workflow.getTitleForStateOnType(state_id, self.doc.portal_type)
        self.assertEqual(state_title, 'nonsense')

    def testGetTitleForStateOnTypeSucceedsWithNonString(self):
        # Related to http://dev.plone.org/plone/ticket/4638
        # Non content objects can pass None or MissingValue.
        state_id = None
        state_title = self.workflow.getTitleForStateOnType(state_id, self.doc.portal_type)
        self.assertEqual(state_title, state_id)

    def testGetTitleForTransitionOnType(self):
        state_id = 'hide'
        state_title = self.workflow.getTitleForTransitionOnType(state_id, self.doc.portal_type)
        self.assertEqual(state_title, 'Make private')

    def testGetTitleForTransitionOnTypeFallsBackOnTransitionId(self):
        state_id = 'nonsense'
        state_title = self.workflow.getTitleForTransitionOnType(state_id, self.doc.portal_type)
        self.assertEqual(state_title, 'nonsense')

    def testGetTitleForTransitionOnTypeSucceedsWithNonString(self):
        # Related to http://dev.plone.org/plone/ticket/4638
        # Non content objects can pass None or MissingValue.
        state_id = None
        state_title = self.workflow.getTitleForTransitionOnType(state_id, self.doc.portal_type)
        self.assertEqual(state_title, state_id)

    def testListWFStatesByTitle(self):
        states = self.workflow.listWFStatesByTitle()
        self.assertEqual(len(states), 7)
        pub_states = [s for s in states if s[1]=='published']
        priv_states = [s for s in states if s[1]=='private']
        pend_states = [s for s in states if s[1]=='pending']
        vis_states = [s for s in states if s[1]=='visible']
        self.assertEqual(len(pub_states), 2)
        self.assertEqual(len(priv_states), 2)
        self.assertEqual(len(pend_states), 1)
        self.assertEqual(len(vis_states), 2)

    def testListWFStatesByTitleFiltersSimilar(self):
        states = self.workflow.listWFStatesByTitle(filter_similar=True)
        self.assertEqual(len(states), 4)
        pub_states = [s for s in states if s[1]=='published']
        priv_states = [s for s in states if s[1]=='private']
        pend_states = [s for s in states if s[1]=='pending']
        vis_states = [s for s in states if s[1]=='visible']
        self.assertEqual(len(pub_states), 1)
        self.assertEqual(len(priv_states), 1)
        self.assertEqual(len(pend_states), 1)
        self.assertEqual(len(vis_states), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkflowTool))
    return suite

if __name__ == '__main__':
    framework()
