# -*- coding: utf-8 -*-
from plone.app.layout.links.viewlets import RSSViewlet
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from zope.component import getUtility


class TestRSSViewletView(ViewletsTestCase):

    def test_RSSViewlet(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'news')
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSyndicationSettings)
        if settings.allowed:
            # make sure syndication is disabled
            settings.allowed = False
        request = self.app.REQUEST
        viewlet = RSSViewlet(self.portal, request, None, None)
        viewlet.update()
        result = viewlet.render()
        self.assertEqual(result.strip(), '')
        settings.allowed = True
        settings.site_rss_items = (self.portal.news.UID(),)
        request = self.app.REQUEST
        viewlet = RSSViewlet(self.portal, request, None, None)
        viewlet.update()
        result = viewlet.render()
        self.assertFalse("<link" not in result)
        self.assertFalse("http://nohost/plone/atom.xml" not in result)
        self.assertFalse("http://nohost/plone/news/atom.xml" not in result)
