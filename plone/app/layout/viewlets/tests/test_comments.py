from DateTime import DateTime
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.app.layout.viewlets.comments import CommentsViewlet
from Products.CMFCore.utils import getToolByName


class TestCommentsViewletView(ViewletsTestCase):
    """Test the comments viewlet"""
    
    def afterSetUp(self):
        self.setRoles(['Manager', 'Member'])
        self.portal.invokeFactory('Document', 'document')
        disc_tool = getToolByName(self, 'portal_discussion')
        disc_tool.overrideDiscussionFor(self.portal.document, True)
        self.logout()
    
    def _comment_login_url(self):
        viewlet = CommentsViewlet(self.portal.document, self.app.REQUEST, None, None)
        viewlet.update()
        return viewlet.login_url()
    
    def test_existent_login_url(self):
        """Make sure login_url() works when there is a login action defined."""
        self.assertEqual(self._comment_login_url(), 'http://nohost/plone/login')

    def test_anonexistent_login_url(self):
        """Make sure login_url() works when there is no login action defined."""
        getToolByName(self.portal.document, 'portal_actions').user.manage_delObjects(['login'])
        self.assertEqual(self._comment_login_url(), None)

    def test_time_render(self):
        request = self.app.REQUEST
        context = self.portal.document
        dtool = getToolByName(context, 'portal_discussion')
        tb = dtool.getDiscussionFor(context)
        reply_id = tb.createReply(title='Subject', text='Reply text', Creator='tester')

        viewlet = CommentsViewlet(context, request, None, None)
        viewlet.update()
        time = DateTime('2009/10/20 15:00')
        self.assertEqual(viewlet.format_time(time), 'Oct 20, 2009 03:00 PM')

    def test_viewing_uncommented_item_doesnt_create_talkback(self):
        # make sure we avoid creating unnecessary persistent talkbacks
        self.assertFalse(hasattr(self.portal.document, 'talkback'))
        viewlet = CommentsViewlet(self.portal.document, self.app.REQUEST, None, None)
        viewlet.update()
        viewlet.render()
        self.assertFalse(hasattr(self.portal.document, 'talkback'))

def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
