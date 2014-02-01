from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zExceptions import NotFound
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.browser.syndication.adapters import BaseItem


class BaseSyndicationTest(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.syndication = getToolByName(self.portal, 'portal_syndication')
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.invokeFactory('Document', 'doc2')
        self.folder.invokeFactory('File', 'file')
        self.doc1 = self.folder.doc1
        self.doc2 = self.folder.doc2
        self.file = self.folder.file
        #Enable syndication on folder
        registry = getUtility(IRegistry)
        self.site_settings = registry.forInterface(ISiteSyndicationSettings)
        settings = IFeedSettings(self.folder)
        settings.enabled = True
        self.folder_settings = settings


class TestOldSyndicationTool(BaseSyndicationTest):

    def testIsSiteSyndicationAllowed(self):
        # Make sure isSiteSyndicationAllowed returns proper value so that tabs
        # appear
        self.assertTrue(self.syndication.isSiteSyndicationAllowed())
        self.setRoles(['Manager'])
        self.syndication.editProperties(isAllowed=False)
        self.assertTrue(not self.syndication.isSiteSyndicationAllowed())

    def testIsSyndicationAllowed(self):
        # Make sure isSyndicationAllowed returns proper value so that the
        # action appears
        self.assertTrue(self.syndication.isSyndicationAllowed(self.folder))
        self.syndication.disableSyndication(self.folder)
        self.assertFalse(self.syndication.isSyndicationAllowed(self.folder))

    def testGetSyndicatableContent(self):
        content = self.syndication.getSyndicatableContent(self.folder)
        self.assertEqual(len(content), 3)

    def testOwnerCanEnableAndDisableSyndication(self):
        self.setRoles(['Owner'])
        self.syndication.disableSyndication(self.folder)
        self.assertFalse(self.syndication.isSyndicationAllowed(self.folder))
        self.syndication.enableSyndication(self.folder)
        self.assertTrue(self.syndication.isSyndicationAllowed(self.folder))
        self.logout()
        self.assertRaises(Unauthorized, self.syndication.enableSyndication,
                          self.folder)
        self.assertRaises(Unauthorized, self.syndication.disableSyndication,
                          self.folder)


class TestSyndicationUtility(BaseSyndicationTest):

    def test_context_allowed_not_syndicatable(self):
        util = self.doc1.restrictedTraverse('@@syndication-util')
        self.assertEqual(util.context_allowed(), False)

    def test_context_allowed(self):
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.assertEqual(util.context_allowed(), True)

    def test_context_allowed_site_disabled(self):
        self.site_settings.allowed = False
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.assertEqual(util.context_allowed(), False)

    def test_context_enabled(self):
        self.folder_settings.enabled = True
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.assertEqual(util.context_enabled(), True)

    def test_not_context_enabled(self):
        self.folder_settings.enabled = False
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.assertEqual(util.context_enabled(), False)

    def test_context_enabled_site_disabled(self):
        self.site_settings.allowed = False
        self.folder_settings.enabled = True
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.assertEqual(util.context_enabled(), False)

    def test_context_enabled_raises_404(self):
        self.site_settings.allowed = False
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.assertRaises(NotFound, util.context_enabled, True)

    def test_allowed_feed_types(self):
        util = self.folder.restrictedTraverse('@@syndication-util')
        types = util.allowed_feed_types()
        self.assertEqual(len(types), len(self.folder_settings.feed_types))

    def test_site_settings(self):
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.assertTrue(util.site_settings is not None)

    def test_search_rss_enabled(self):
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.site_settings.search_rss_enabled = True
        self.assertEqual(util.search_rss_enabled(), True)

    def test_not_search_rss_enabled_raise_404(self):
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.site_settings.search_rss_enabled = False
        self.assertRaises(NotFound, util.search_rss_enabled, True)

    def test_show_author_info(self):
        self.site_settings.show_author_info = True
        util = self.folder.restrictedTraverse('@@syndication-util')
        self.assertEqual(util.show_author_info(), True)
        self.site_settings.show_author_info = False
        self.assertEqual(util.show_author_info(), False)


class TestSyndicationViews(BaseSyndicationTest):

    def test_valid_feeds(self):
        for _type in self.folder_settings.feed_types:
            self.folder.restrictedTraverse(str(_type))()

    def test_invalid_feed_raises_404(self):
        self.folder_settings.feed_types = ('RSS',)
        self.assertRaises(NotFound, self.folder.restrictedTraverse('rss.xml'))

    def test_search_feed_view(self):
        self.site_settings.search_rss_enabled = True
        self.portal.restrictedTraverse('@@search_rss')()

    def test_search_feed_view_raises_404(self):
        self.site_settings.search_rss_enabled = False
        self.assertRaises(NotFound,
            self.portal.restrictedTraverse('@@search_rss'))

    def test_search_feed_view_raises_404_not_site_root(self):
        self.site_settings.search_rss_enabled = True
        self.assertRaises(NotFound,
            self.folder.restrictedTraverse('@@search_rss'))


class TestSyndicationFeedAdapter(BaseSyndicationTest):

    def afterSetUp(self):
        super(TestSyndicationFeedAdapter, self).afterSetUp()
        self.feed = IFeed(self.folder)
        self.feeddatadoc = BaseItem(self.doc1, self.feed)
        self.feeddatafile = BaseItem(self.file, self.feed)

    def test_link_on_folder(self):
        self.assertEqual(self.feed.link, self.folder.absolute_url())

    def test_link_on_file(self):
        self.assertEqual(self.feeddatafile.link,
            self.file.absolute_url() + '/view')

    def test_items(self):
        self.assertEqual(len(self.feed._brains()), 3)
        self.assertEqual(len([i for i in self.feed.items]), 3)

    def test_max_items(self):
        self.feed.settings.max_items = 2
        self.assertEqual(len([i for i in self.feed.items][:self.feed.limit]),
                                                                           2)

    def test_has_enclosure(self):
        self.assertEqual(self.feeddatadoc.has_enclosure, False)
        self.assertEqual(self.feeddatafile.has_enclosure, True)
