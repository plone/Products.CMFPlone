#
# Test queryCatalog and plone search forms
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base


class TestQueryCatalog(PloneTestCase.PloneTestCase):
    """Test queryCatalog script.
    
    Test function of queryCatalog script, **not** the
    functionality of the catalog itself. Therefore, we'll replace
    the actual call to the catalog to a dummy routine that just
    returns the catalog search dictionary so we can examine what
    would be searched.
    """

    def dummyCatalog(self, query_dict):
        return query_dict
    
    def afterSetUp(self):
        self.portal.portal_catalog.__call__ = self.dummyCatalog

    def testEmptyRequest(self):
        request = {}
        self.assertEqual(self.folder.queryCatalog(request), [])
        #self.failUnless(hasattr(aq_base(self.catalog), 'plone_lexicon'))
        #self.assertEqual(self.catalog.plone_lexicon.meta_type, 'ZCTextIndex Lexicon')

    def testNonexistantIndex(self):
        request = {'foo':'bar'}
        self.assertEqual(self.folder.queryCatalog(request), [])

    def testNonexistantIndex(self):
        request = {'foo':'bar'}
        self.assertEqual(self.folder.queryCatalog(request), [])

    def testRealIndex(self):
        request = {'SearchableText':'bar'}
        self.assertEqual(self.folder.queryCatalog(request), {'SearchableText':'bar'})

    def testTwoIndexes(self):
        request = {'SearchableText':'bar','foo':'bar'}
        self.assertEqual(self.folder.queryCatalog(request), {'SearchableText':'bar'})

    def testRealIndexes(self):
        request = {'SearchableText':'bar','Subject':'bar'}
        self.assertEqual(self.folder.queryCatalog(request), request )

    def testOnlySort(self):
        # if we only sort, we shouldn't actually call the catalog
        request = {'sort_on':'foozle'}
        self.assertEqual(self.folder.queryCatalog(request), [])
        request = {'sort_order':'foozle','sort_on':'foozle'}
        self.assertEqual(self.folder.queryCatalog(request), [])
        request = {'sort_order':'foozle'}
        self.assertEqual(self.folder.queryCatalog(request), [])

    def testOnlyUsage(self):
        request = {'date_usage':'range:min'}
        self.assertEqual(self.folder.queryCatalog(request), [])

    def testRealWithUsage(self):
        request = {'modified':'2004-01-01','modified_usage':'range:min'}
        expected = {'modified': {'query': '2004-01-01', 'range': 'min'}}
        self.assertEqual(self.folder.queryCatalog(request), expected)


class TestQueryCatalogQuoting(PloneTestCase.PloneTestCase):
    """Test logic quoting features queryCatalog script.
    
    Test function of queryCatalog script, **not** the
    functionality of the catalog itself. Therefore, we'll replace
    the actual call to the catalog to a dummy routine that just
    returns the catalog search dictionary so we can examine what
    would be searched.
    """

    def dummyCatalog(self, query_dict):
        return query_dict
    
    def afterSetUp(self):
        self.portal.portal_catalog.__call__ = self.dummyCatalog

    def testQuotingNone(self):
        request = {'SearchableText':'Hello Joel'}
        expected = request
        self.assertEqual(self.folder.queryCatalog(request, quote_logic=1), expected)

    def testQuotingNotNeeded(self):
        request = {'SearchableText':'Hello or Joel'}
        expected = request
        self.assertEqual(self.folder.queryCatalog(request, quote_logic=1), expected)

    def testQuotingNotNeededWithNot(self):
        request = {'SearchableText':'Hello or not Joel'}
        expected = request
        self.assertEqual(self.folder.queryCatalog(request, quote_logic=1), expected)

    def testQuotingRequiredToEscape(self):
        request = {'SearchableText':'Hello Joel Or'}
        expected = {'SearchableText':'Hello Joel "Or"'}
        self.assertEqual(self.folder.queryCatalog(request, quote_logic=1), expected)

    def testQuotingRequiredToEscapeOptionOff(self):
        request = {'SearchableText':'Hello Joel Or'}
        expected = request
        self.assertEqual(self.folder.queryCatalog(request), expected)

    def testQuotingWithLeadingNot(self):
        request = {'SearchableText':'Not Hello Joel'}
        expected = request
        self.assertEqual(self.folder.queryCatalog(request), expected)

    def testEmptyItem(self):
        request = {'SearchableText':''}
        expected = request
        self.assertEqual(self.folder.queryCatalog(request), expected)


AddPortalTopics = 'Add portal topics'

class TestSearchForms(PloneTestCase.PloneTestCase):
    """Render all forms related to queryCatalog"""

    def testRenderSearchForm(self):
        self.portal.search_form()

    def testRenderSearchResults(self):
        self.portal.search()

    def testRenderSearchRSS(self):
        self.portal.search_rss(self.portal, self.app.REQUEST)

    def testRenderTopicView(self):
        self.setPermissions(AddPortalTopics)
        self.folder.invokeFactory('Topic', id='topic')
        self.folder.topic.topic_view()


if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestQueryCatalog))
        suite.addTest(makeSuite(TestQueryCatalogQuoting))
        suite.addTest(makeSuite(TestSearchForms))
        return suite
