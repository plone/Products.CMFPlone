#
# Test the RecentPortlet View
#

from Products.CMFPlone.tests import PloneTestCase

# BBB Plone 4.0
import warnings
showwarning = warnings.showwarning
warnings.showwarning = lambda *a, **k: None
# ignore deprecation warnings on import
from Products.CMFPlone.browser.interfaces import IRecentPortlet
from Products.CMFPlone.browser.portlets.recent import RecentPortlet
# restore warning machinery
warnings.showwarning = showwarning


class TestRecentPortletView(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.url = self.portal.portal_url
        #self.recent = self.portal.recent
        self.workflow = self.portal.portal_workflow
        self.setupAuthenticator()

    def testImplementsIRecentPortlet(self):
        """RecentPortlet must implement IRecentPortlet"""
        self.failUnless(IRecentPortlet.implementedBy(RecentPortlet))

    def testRecentResults(self):
        """RecentPortlet.results() must return recently updated content"""
        self.portal.portal_catalog.manage_catalogClear()
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Document', id='testpage', text='data', title='Foo')
        self.workflow.doActionFor(self.folder.testpage, 'publish')
        view = RecentPortlet(self.portal, self.app.REQUEST)
        result = view.results()
        self.failUnlessEqual(len(result), 1)
        self.failUnlessEqual(result[0].getId, 'testpage')

    def testNoRecent(self):
        """RecentPortlet.results() must return no content when no recent items"""
	    # clear out the catalog to guarantee no results
        self.portal.portal_catalog.manage_catalogClear()
        view = RecentPortlet(self.portal, self.app.REQUEST)
        result = view.results()
        return result
        self.failUnlessEqual(len(result), 0)

    def testRecentResultsPrivate(self):
        """RecentPortlet.results() must return private items"""
        self.portal.portal_catalog.manage_catalogClear()
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Document', id='testpage', text='data', title='Foo')
        self.workflow.doActionFor(self.folder.testpage, 'hide')
        view = RecentPortlet(self.portal, self.app.REQUEST)
        result = view.results()
        self.failUnlessEqual(len(result), 1)
        self.failUnlessEqual(result[0].getId, 'testpage')

    def testRecentResultsPublicDraft(self):
        """RecentPortlet.results() must return public draft items"""
        self.portal.portal_catalog.manage_catalogClear()
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Document', id='testpage', text='data', title='Foo')
        view = RecentPortlet(self.portal, self.app.REQUEST)
        result = view.results()
        self.failUnlessEqual(len(result), 1)
        self.failUnlessEqual(result[0].getId, 'testpage')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRecentPortletView))
    return suite

