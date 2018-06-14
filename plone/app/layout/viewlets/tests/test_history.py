# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.app.layout.viewlets.content import WorkflowHistoryViewlet
from plone.app.layout.viewlets.tests.base import ViewletsFunctionalTestCase
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_ID


class TestWorkflowHistoryViewlet(ViewletsFunctionalTestCase):

    def setUp(self):
        super(TestWorkflowHistoryViewlet, self).setUp()
        # add document, perform transition, set history for non-existent
        # member and also None (anonymous)
        self.folder.invokeFactory('Document', 'd1')

    def addMember(self, username, roles=('Member',)):
        self.portal.portal_membership.addMember(username, 'secret', roles, [])

    def delMember(self, username):
        self.portal.portal_membership.deleteMembers([username])

    def test_initHistory(self):
        request = self.app.REQUEST
        context = getattr(self.folder, 'd1')
        viewlet = WorkflowHistoryViewlet(context, request, None, None)
        viewlet.update()
        history = viewlet.workflowHistory()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['action'], None)

    def test_transitionHistory(self):
        wf_tool = self.portal.portal_workflow
        request = self.app.REQUEST
        context = getattr(self.folder, 'd1')
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        wf_tool.doActionFor(context, 'publish')

        viewlet = WorkflowHistoryViewlet(context, request, None, None)
        viewlet.update()

        history = viewlet.workflowHistory()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['action'], 'publish')

        # add a temporary user to perform a transition
        self.addMember('tempuser', roles=('Member', 'Manager'))
        login(self.portal, 'tempuser')
        wf_tool.doActionFor(context, action='retract', actor=None)
        logout()

        login(self.portal, TEST_USER_NAME)

        # remove the user
        self.delMember('tempuser')

        # if the user that performed the transition no longer exists, the link
        # shouldn't be included.
        viewlet = WorkflowHistoryViewlet(context, request, None, None)
        viewlet.update()
        history = viewlet.workflowHistory()

        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['actor_home'], '')


class TestContentHistoryViewlet(ViewletsFunctionalTestCase):

    def setUp(self):
        super(TestContentHistoryViewlet, self).setUp()
        # add document, perform transition, set history for non-existent
        # member and also None (anonymous)
        self.folder.invokeFactory('Document', 'd1')

    def test_initialHistory(self):
        request = self.app.REQUEST
        context = getattr(self.folder, 'd1')
        viewlet = ContentHistoryViewlet(context, request, None, None)
        viewlet.update()
        self.assertEqual(len(viewlet.revisionHistory()), 1)

    def test_revisionHistory(self):
        repo_tool = self.portal.portal_repository
        request = self.app.REQUEST
        context = getattr(self.folder, 'd1')
        viewlet = ContentHistoryViewlet(context, request, None, None)
        viewlet.update()

        # after creating the item the is a first revision
        history = viewlet.revisionHistory()
        self.assertEqual(len(history), 1)

        repo_tool.save(context, comment='Initial Revision')
        viewlet.update()
        history = viewlet.revisionHistory()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['comments'], 'Initial Revision')

        repo_tool.save(context, comment='Second Revision')
        viewlet.update()
        history = viewlet.revisionHistory()
        self.assertTrue(
            'http://nohost/plone/Members/test_user_1_/d1/@@history?one=2&two=1'
            in history[0]['diff_previous_url']
        )

        # check diff link does not appear if content is not diffable
        diff_tool = self.portal.portal_diff
        diff_tool.setDiffForPortalType('Document', {})
        viewlet.update()
        history = viewlet.revisionHistory()
        self.assertFalse('diff_previous_url' in history[0])

    def test_revertAbility(self):
        # check revert URL is generated only if the user has the appropriate
        # permission
        repo_tool = self.portal.portal_repository
        request = self.app.REQUEST
        context = getattr(self.folder, 'd1')
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        repo_tool.save(context, comment='Initial Revision')
        repo_tool.save(context, comment='Second Revision')

        viewlet = ContentHistoryViewlet(context, request, None, None)

        viewlet.update()
        history = viewlet.revisionHistory()
        self.assertTrue(
            'http://nohost/plone/Members/test_user_1_/d1/revertversion' in history[0]['revert_url'])  # noqa

        self.portal.manage_permission(
            'CMFEditions: Revert to previous versions', [], False)

        viewlet.update()
        history = viewlet.revisionHistory()
        self.assertEqual(history[0]['revert_url'], None)
