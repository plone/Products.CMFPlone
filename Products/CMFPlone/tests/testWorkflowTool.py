#
# Tests the workflow tool
#

from zope.interface import directlyProvides
from zope.component import provideAdapter, getGlobalSiteManager

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests.dummy import Dummy, DummyWorkflowChainAdapter
from Products.CMFDefault.interfaces import IDocument
from Products.CMFCore.interfaces import IWorkflowTool

default_user = PloneTestCase.default_user

# INFO - Ugh...Rather than use and update ambiguous numbers,
# we maintain a mapping of the various workflows to stats
# though there are some obvious downsides to this, it's better than just
# asserting that there are X published states in all workflows, etc.
workflow_dict = {
      'folder_workflow':('private','published','visible',)
    , 'intranet_folder_workflow':('internal','private',)
    , 'intranet_workflow':('internal','internally_published','pending',
                           'private','external',)
    , 'one_state_workflow':('published',)
    , 'plone_workflow':('pending','private','published','visible',)
    , 'simple_publication_workflow':('private','published','pending',)
    , 'comment_review_workflow':('pending', 'published',)
}
# then we join all states into one master list
all_states = []
for states in workflow_dict.values():
    all_states += list(states)

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
        self.failUnless('url' in trans[0])
        # Test that url has filled in string substitutions for content url
        self.failUnless('http://' in trans[0]['url'])

    def testGetTransitionsForProvidesDescription(self):
        trans = self.workflow.getTransitionsFor(self.doc)
        self.assertEqual(len(trans), 2)
        self.failUnless('description' in trans[0])

    def testGetTitleForStateOnType(self):
        state_id = self.workflow.getInfoFor(self.doc, 'review_state', '')
        state_title = self.workflow.getTitleForStateOnType(state_id, self.doc.portal_type)
        self.assertEqual(state_id, 'visible')
        self.assertEqual(state_title.lower(), 'public draft')

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
        self.assertEqual(len(states), len(all_states))
        pub_states = [s for s in states if s[1]=='published']
        priv_states = [s for s in states if s[1]=='private']
        pend_states = [s for s in states if s[1]=='pending']
        vis_states = [s for s in states if s[1]=='visible']
        external_states = [s for s in states if s[1]=='external']
        internal_states = [s for s in states if s[1]=='internal']
        internal_pub_states = [s for s in states
                                 if s[1]=='internally_published']

        self.assertEqual(len(pub_states), all_states.count('published'))
        self.assertEqual(len(priv_states), all_states.count('private'))
        self.assertEqual(len(pend_states), all_states.count('pending'))
        self.assertEqual(len(vis_states), all_states.count('visible'))
        self.assertEqual(len(external_states), all_states.count('external'))
        self.assertEqual(len(internal_states), all_states.count('internal'))
        self.assertEqual(len(internal_pub_states),
                         all_states.count('internally_published'))

    def testAdaptationBasedWorkflowOverride(self):
        # We take a piece of dummy content and register a dummy
        # workflow chain adapter for it.
        content = Dummy()
        directlyProvides(content, IDocument)
        provideAdapter(DummyWorkflowChainAdapter,
                        adapts=(IDocument, IWorkflowTool))
        self.assertEqual(self.workflow.getChainFor(content),
                         ('Static Workflow',))
        # undo our registration so we don't break tests
        components = getGlobalSiteManager()
        components.unregisterAdapter(DummyWorkflowChainAdapter,
                                     required=(IDocument, IWorkflowTool))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkflowTool))
    return suite
