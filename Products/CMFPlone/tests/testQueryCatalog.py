# Test queryCatalog and plone search forms

from zope.component import getMultiAdapter
from Products.CMFPlone.tests import PloneTestCase

from Products.ZCTextIndex.ParseTree import ParseError
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zExceptions import NotFound
import types


class TestQueryCatalog(PloneTestCase.PloneTestCase):
    """Test queryCatalog script.

    Test function of queryCatalog script, **not** the
    functionality of the catalog itself. Therefore, we'll replace
    the actual call to the catalog to a dummy routine that just
    returns the catalog search dictionary so we can examine what
    would be searched.
    """

    def dummyCatalog(self, REQUEST=None, **kw):
        return kw

    def stripStuff(self, query_dict):
        # strip portal_types and show_inactive parameter which is
        # auto-set with types blacklisting. Useful to simplify test
        # assertions when we don't care
        if type(query_dict) == types.DictType:
            for ignore in ['portal_type', 'show_inactive']:
                if ignore in query_dict:
                    del query_dict[ignore]
        return query_dict

    def afterSetUp(self):
        self.portal.portal_catalog.__call__ = self.dummyCatalog

    def testEmptyRequest(self):
        request = {}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request)), [])

    def testNonexistantIndex(self):
        request = {'foo': 'bar'}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request)), [])

    def testRealIndex(self):
        request = {'SearchableText': 'bar'}
        self.assertEqual(self.stripStuff(self.folder.queryCatalog(request)),
                            {'SearchableText': 'bar'})

    def testTwoIndexes(self):
        request = {'SearchableText': 'bar', 'foo': 'bar'}
        self.assertEqual(self.stripStuff(self.folder.queryCatalog(request)),
                            {'SearchableText': 'bar'})

    def testRealIndexes(self):
        request = {'SearchableText': 'bar', 'Subject': 'bar'}
        self.assertEqual(self.stripStuff(self.folder.queryCatalog(request)),
                            request)

    def testOnlySort(self):
        # if we only sort, we shouldn't actually call the catalog
        request = {'sort_on': 'foozle'}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request)), [])
        request = {'sort_order': 'foozle', 'sort_on': 'foozle'}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request)), [])
        request = {'sort_order': 'foozle'}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request)), [])

    def testOnlyUsage(self):
        request = {'date_usage': 'range:min'}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request)), [])

    def testRealWithUsage(self):
        request = {'modified': '2004-01-01', 'modified_usage': 'range:min'}
        expected = {'modified': {'query': '2004-01-01', 'range': 'min'}}
        self.assertEqual(self.stripStuff(self.folder.queryCatalog(request)),
                            expected)

    def testSortLimit(self):
        # the script ignored 'sort_limit'; test to show it no longer does.
        request = {'SearchableText': 'bar',
                   'sort_on': 'foozle',
                   'sort_limit': 50}
        self.assertEqual(self.stripStuff(self.folder.queryCatalog(request)),
                            request)

    def testBlacklistedTypes(self):
        request = {'SearchableText': 'a*'}
        siteProps = self.portal.portal_properties.site_properties
        siteProps.types_not_searched = ['Event', 'Unknown Type']
        qry = self.folder.queryCatalog(request, use_types_blacklist=True)
        self.assertTrue('Document' in qry['portal_type'])
        self.assertTrue('Event' not in qry['portal_type'])

    def testNavigationRoot(self):
        request = {'SearchableText': 'a*'}
        ntp = self.portal.portal_properties.navtree_properties
        ntp.root = '/'
        qry = self.folder.queryCatalog(request, use_navigation_root=True)
        self.assertEquals('/'.join(self.portal.getPhysicalPath()), qry['path'])
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', 'foo')
        ntp.root = '/foo'
        qry = self.folder.queryCatalog(request, use_navigation_root=True)
        self.assertEquals('/'.join(self.portal.foo.getPhysicalPath()),
                          qry['path'])

    def testNavigationRootDoesNotOverrideExplicitPath(self):
        request = {'SearchableText': 'a*', 'path': '/yyy/zzz'}
        ntp = self.portal.portal_properties.navtree_properties
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Folder', 'foo')
        ntp.root = '/foo'
        qry = self.folder.queryCatalog(request, use_navigation_root=True)
        self.assertEquals('/yyy/zzz', qry['path'])


class TestQueryCatalogQuoting(PloneTestCase.PloneTestCase):
    """Test logic quoting features queryCatalog script.

    Test function of queryCatalog script, **not** the
    functionality of the catalog itself. Therefore, we'll replace
    the actual call to the catalog to a dummy routine that just
    returns the catalog search dictionary so we can examine what
    would be searched.
    """

    def dummyCatalog(self, REQUEST=None, **kw):
        return kw

    def stripStuff(self, query_dict):
        # strip portal_types and show_inactive parameter which is
        # auto-set with types blacklisting. Useful to simplify test
        # assertions when we don't care
        if type(query_dict) == types.DictType:
            for ignore in ['portal_type', 'show_inactive']:
                if ignore in query_dict:
                    del query_dict[ignore]
        return query_dict

    def afterSetUp(self):
        self.portal.portal_catalog.__call__ = self.dummyCatalog

    def testQuotingNone(self):
        request = {'SearchableText': 'Hello Joel'}
        expected = request
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request, quote_logic=1)),
            expected)

    def testQuotingNotNeeded(self):
        request = {'SearchableText': 'Hello or Joel'}
        expected = request
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request, quote_logic=1)),
            expected)

    def testQuotingNotNeededWithNot(self):
        request = {'SearchableText': 'Hello or not Joel'}
        expected = request
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request, quote_logic=1)),
            expected)

    def testQuotingRequiredToEscape(self):
        request = {'SearchableText': 'Hello Joel Or'}
        expected = {'SearchableText': 'Hello Joel "Or"'}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request, quote_logic=1)),
            expected)

    def testQuotingRequiredToEscapeOptionOff(self):
        request = {'SearchableText': 'Hello Joel Or'}
        expected = request
        self.assertEqual(self.stripStuff(self.folder.queryCatalog(request)),
                         expected)

    def testQuotingWithLeadingNot(self):
        request = {'SearchableText': 'Not Hello Joel'}
        expected = request
        self.assertEqual(self.stripStuff(self.folder.queryCatalog(request)),
                         expected)

    def testEmptyItem(self):
        request = {'SearchableText': ''}
        # queryCatalog will return empty result without calling the catalog
        # tool
        expected = []
        self.assertEqual(self.stripStuff(self.folder.queryCatalog(request)),
                         expected)

    def testEmptyItemShowAll(self):
        request = {'SearchableText': ''}
        # Catalog gets a blank search, and returns the empty dict
        expected = {}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request, show_all=1)),
            expected)

    def testBadCharsAreQuoted(self):
        request = {'SearchableText': 'context(1)'}
        # Catalog gets ( or ) in search and quotes them to avoid parse error
        expected = {'SearchableText': 'context"("1")"'}
        self.assertEqual(
            self.stripStuff(self.folder.queryCatalog(request)),
            expected)


class TestQueryCatalogParseError(PloneTestCase.PloneTestCase):
    """Checks that the queryCatalog script returns an empty result set
       in case of ZCTextIndex ParseErrors.

       This testcase uses the real catalog, not a stub.
    """

    def afterSetUp(self):
        self.folder.invokeFactory('Document', id='doc', text='foo bar baz')

    def testSearchableText(self):
        request = {'SearchableText': 'foo'}
        # We expect a non-empty result set
        self.assertTrue(self.portal.queryCatalog(request))

    def testParseError(self):
        # ZCTextIndex raises ParseError
        self.assertRaises(ParseError, self.portal.portal_catalog,
                          SearchableText='-foo')

    def testQueryCatalogParseError(self):
        request = {'SearchableText': '-foo'}
        # ZCTextIndex raises ParseError which translates to empty result
        expected = []
        self.assertEqual(self.portal.queryCatalog(request), expected)

    def testQueryCatalogParseError3050(self):
        # http://dev.plone.org/plone/ticket/3050
        request = {'SearchableText': 'AND'}
        # ZCTextIndex raises ParseError which translates to empty result
        expected = []
        self.assertEqual(self.portal.queryCatalog(request), expected)


AddPortalTopics = 'Add portal topics'


class TestSearchForms(PloneTestCase.PloneTestCase):
    """Render all forms related to queryCatalog"""

    def testRenderSearchForm(self):
        searchView = getMultiAdapter((self.portal, self.app.REQUEST),
                                     name="search")
        searchView()

    def testRenderSearchRSS(self):
        searchRssView = getMultiAdapter((self.portal, self.app.REQUEST),
                                        name="search_rss")
        searchRssView()

    def testSearchGives404WhenDisabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSyndicationSettings)
        settings.search_rss_enabled = False
        searchRssView = getMultiAdapter((self.portal, self.app.REQUEST),
                                        name="search_rss")
        self.assertRaises(NotFound, searchRssView)
