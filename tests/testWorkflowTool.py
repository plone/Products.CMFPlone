#
# Tests the workflow tool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.WorkflowCore import WorkflowException


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

    def testListWFStates(self):
        states = self.workflow.listWFStates()
        self.assertEqual(len(states), 7)
        pub_states = [s for s in states if s.id=='published']
        priv_states = [s for s in states if s.id=='private']
        pend_states = [s for s in states if s.id=='pending']
        vis_states = [s for s in states if s.id=='visible']
        self.assertEqual(len(pub_states), 2)
        self.assertEqual(len(priv_states), 2)
        self.assertEqual(len(pend_states), 1)
        self.assertEqual(len(vis_states), 2)

    def testListWFStatesFiltersSimilar(self):
        states = self.workflow.listWFStates(filter_similar=True)
        self.assertEqual(len(states), 4)
        pub_states = [s for s in states if s.id=='published']
        priv_states = [s for s in states if s.id=='private']
        pend_states = [s for s in states if s.id=='pending']
        vis_states = [s for s in states if s.id=='visible']
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
