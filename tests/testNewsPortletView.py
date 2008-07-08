#
# Tests the NewsPortlet View
#

from Products.CMFPlone.tests import PloneTestCase

# BBB Plone 4.0
import warnings
showwarning = warnings.showwarning
warnings.showwarning = lambda *a, **k: None
# ignore deprecation warnings on import
from Products.CMFPlone.browser.interfaces import INewsPortlet
from Products.CMFPlone.browser.portlets.news import NewsPortlet
# restore warning machinery
warnings.showwarning = showwarning


class TestNewsPortletView(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.url = self.portal.portal_url
        self.news = self.portal.news
        self.workflow = self.portal.portal_workflow
        self.setupAuthenticator()

    def testImplementsINewsPortlet(self):
        """NewsPortlet must implement INewsPortlet"""
        self.failUnless(INewsPortlet.implementedBy(NewsPortlet))

    def testNewsItems(self):
        """NewsPortlet.published_news_items() must return published News Items"""
        self.setRoles(['Manager'])
        self.folder.invokeFactory('News Item', id='newsitem', text='data', title='Foo')
        self.workflow.doActionFor(self.folder.newsitem, 'publish')
        view = NewsPortlet(self.portal, self.app.REQUEST)
        result = view.published_news_items()
        self.failUnlessEqual(len(result), 1)
        self.failUnlessEqual(result[0].getId, 'newsitem')

    def testUnpublishedNewsItems(self):
        """NewsPortlet.published_news_items() must not return unpublished News Items"""
        self.folder.invokeFactory('News Item', id='newsitem', text='data', title='Foo')
        view = NewsPortlet(self.portal, self.app.REQUEST)
        result = view.published_news_items()
        self.failUnlessEqual(len(result), 0)

    def testNoNewsItems(self):
        """NewsPortlet.published_news_items() must return empty list if no News Items"""
        view = NewsPortlet(self.portal, self.app.REQUEST)
        result = view.published_news_items()
        self.failUnlessEqual(len(result), 0)

    def testAllNewsLink(self):
        """NewsPortlet.all_news_link() must return URL of 'news' folder if it exists"""
        view = NewsPortlet(self.portal, self.app.REQUEST)
        url = view.all_news_link()
        self.failUnlessEqual(url, self.portal.absolute_url()+'/news')

    def testAllNewsLinkNoNewsFolder(self):
        """
        NewsPortlet.all_news_link() must return URL of 'newslisting'
        template if 'news' does not exist
        """
        # We must have permission to delete objects
        self.setRoles(('Manager',))
        self.portal.manage_delObjects(['news'])
        view = NewsPortlet(self.portal, self.app.REQUEST)
        url = view.all_news_link()
        self.failUnlessEqual(url, self.portal.absolute_url()+'/news_listing')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNewsPortletView))
    return suite
