from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.app.layout.links.viewlets import RSSViewlet


class TestRSSViewletView(ViewletsTestCase):
    """
    Test the document by line viewlet
    """

    def afterSetUp(self):
        pass

    def test_RSSViewlet(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSyndicationSettings)
        if settings.allowed:
            # make sure syndication is disabled
            self.loginAsPortalOwner()
            settings.allowed = False
            self.logout()
        request = self.app.REQUEST
        viewlet = RSSViewlet(self.portal, request, None, None)
        viewlet.update()
        result = viewlet.render()
        self.assertEqual(result.strip(), '')
        self.loginAsPortalOwner()
        settings.allowed = True
        settings.site_rss_items = (self.portal.news.UID(),)
        self.logout()
        request = self.app.REQUEST
        viewlet = RSSViewlet(self.portal, request, None, None)
        viewlet.update()
        result = viewlet.render()
        self.assertFalse("<link" not in result)
        self.assertFalse("http://nohost/plone/atom.xml" not in result)
        self.assertFalse("http://nohost/plone/news/atom.xml" not in result)
