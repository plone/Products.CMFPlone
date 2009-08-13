import unittest
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
        self.assertEqual(self._comment_login_url(), 'http://nohost/plone/login_form')

    def test_anonexistent_login_url(self):
        """Make sure login_url() works when there is no login action defined."""
        getToolByName(self.portal.document, 'portal_actions').user.manage_delObjects(['login'])
        self.assertEqual(self._comment_login_url(), None)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCommentsViewletView))
    return suite
