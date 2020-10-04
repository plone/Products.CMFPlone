import sys
import time
import unittest

from DateTime import DateTime

from plone.app.testing import TEST_USER_NAME, TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from Products.CMFPlone.interfaces import ISearchSchema

from plone.app.contentlisting.interfaces import IContentListing
from plone.app.textfield import RichTextValue

from zope.configuration import xmlconfig
from zope.interface import alsoProvides
from zope.publisher.browser import setDefaultSkin
from z3c.form.interfaces import IFormLayer
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.HTTPRequest import HTTPRequest

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.testing import z2


def test_request():
    """
    make request suitable for browser views and Zope2 security.
    """
    response = HTTPResponse(stdout=sys.stdout)
    request = HTTPRequest(
        sys.stdin,
        {
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '80',
            'REQUEST_METHOD': 'GET',
        },
        response
    )
    request['ACTUAL_URL'] = 'http://nohost/plone'
    setDefaultSkin(request)
    alsoProvides(request, IFormLayer)  # suitable for testing z3c.form views
    return request


class SearchLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import plone.app.contentlisting
        xmlconfig.file('configure.zcml',
                       plone.app.contentlisting, context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        if 'Document' not in portal.portal_types:
            applyProfile(portal, 'plone.app.contenttypes:default')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        for i in range(0, 12):
            portal.invokeFactory(
                'Document',
                'my-page' + str(i),
                text=RichTextValue(
                    'spam spam ham eggs', 'text/html', 'text/x-html-safe'),
            )
            # Sleep before creating the next one, otherwise ordering by date is
            # not deterministic.
            time.sleep(0.1)
        setRoles(portal, TEST_USER_ID, ['Member'])

        # Commit so that the test browser sees these objects
        import transaction
        transaction.commit()


SEARCH_FIXTURE = SearchLayer()
SEARCH_INTEGRATION_TESTING = IntegrationTesting(bases=(SEARCH_FIXTURE, ),
                                                name="Search:Integration")


class SearchTestCase(unittest.TestCase):
    """We use this base class for all tahe tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit
    test cases.
    """
    layer = SEARCH_INTEGRATION_TESTING


class TestSection(SearchTestCase):
    """The name of the class should be meaningful. This may be a class that
    tests the installation of a particular product.
    """

    def test_breadcrumbs(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        portal.invokeFactory('Document', 'first_level_document')
        portal.invokeFactory('Folder', 'first_level_folder',
                             title='First Level Folder')
        first_level_folder = portal.first_level_folder
        first_level_folder.invokeFactory('Document', 'second_level_document')
        first_level_folder.invokeFactory('Folder', 'second_level_folder')
        second_level_folder = first_level_folder.second_level_folder
        second_level_folder.invokeFactory('Document', 'third_level_document')

        view = portal.restrictedTraverse('@@search')

        def crumbs(item):
            return view.breadcrumbs(IContentListing([item])[0])

        # return None for first_level objects
        title = crumbs(portal.first_level_document)
        self.assertEqual(title, None)

        title = crumbs(first_level_folder)
        self.assertEqual(title, None)

        # return section for objects deeper in the hierarchy
        title = crumbs(first_level_folder.second_level_document)[0]['Title']
        self.assertEqual(title, 'First Level Folder')

        title = crumbs(second_level_folder)[0]['Title']
        self.assertEqual(title, 'First Level Folder')

        title = crumbs(second_level_folder.third_level_document)[0]['Title']
        self.assertEqual(title, 'First Level Folder')

    def test_blacklisted_types_in_results(self):
        """Make sure we don't break types' blacklisting in the new search
        results view.
        """
        portal = self.layer['portal']
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        q = {'SearchableText': 'spam'}
        res = portal.restrictedTraverse('@@search').results(query=q,
                                                            batch=False)
        self.assertTrue('my-page1' in [r.getId() for r in res],
                        'Test document is not found in the results.')

        # Now let's exclude 'Document' from the search results:
        search_settings.types_not_searched = ('Document',)
        res = portal.restrictedTraverse('@@search').results(query=q,
                                                            batch=False)
        self.assertFalse(
            'my-page1' in [r.getId() for r in res],
            'Blacklisted type "Document" has been found in search results.')

    def test_default_search_order_relevance(self):
        """Test default order as relevance."""
        portal = self.layer['portal']
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        self.assertEqual(search_settings.sort_on, 'relevance')

        q = {'SearchableText': 'spam'}
        view = portal.restrictedTraverse('@@search')
        self.assertEqual(view.default_sort_on, 'relevance')
        res = view.results(query=q)
        ids = [r.getId() for r in res]
        expected = [
            'my-page11', 'my-page10', 'my-page9', 'my-page8', 'my-page7',
            'my-page6', 'my-page5', 'my-page4', 'my-page3', 'my-page2'
        ]
        self.assertEqual(ids, expected)

    def test_default_search_order_date(self):
        """Test default order as date."""
        portal = self.layer['portal']

        # Change one object date to see if order change works
        mp5 = portal['my-page5']
        mp5.setEffectiveDate(DateTime() + 1)
        mp5.reindexObject()

        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        search_settings.sort_on = 'Date'
        q = {'SearchableText': 'spam'}
        view = portal.restrictedTraverse('@@search')
        self.assertEqual(view.default_sort_on, 'Date')
        res = view.results(query=q)
        ids = [r.getId() for r in res]
        expected = [
            'my-page11', 'my-page10', 'my-page9', 'my-page8', 'my-page7',
            'my-page6', 'my-page4', 'my-page3', 'my-page2', 'my-page1'
        ]
        self.assertEqual(ids, expected)

    def test_default_search_order_alphabetic(self):
        """Test default order as alphabetic."""
        portal = self.layer['portal']

        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        search_settings.sort_on = 'sortable_title'
        q = {'SearchableText': 'spam'}
        view = portal.restrictedTraverse('@@search')
        self.assertEqual(view.default_sort_on, 'sortable_title')
        res = view.results(query=q)
        ids = [r.getId() for r in res]
        expected = [
            'my-page0', 'my-page1', 'my-page2', 'my-page3', 'my-page4',
            'my-page5', 'my-page6', 'my-page7', 'my-page8', 'my-page9'
        ]
        self.assertEqual(ids, expected)

    def test_filter_empty(self):
        """Test filtering for empty query"""
        portal = self.layer['portal']
        req = test_request()
        # Search.filter_query() will get SearchableText from form if not
        # passed in explicit query argument:
        req.form['SearchableText'] = 'spam'
        view = getMultiAdapter((portal, req), name='search')
        res = view.results(batch=False)
        self.assertTrue('my-page1' in [r.getId() for r in res],
                        'Test document is not found in the results.')
        # filter_query() will return None on invalid query (no real indexes):
        req = test_request()
        req.form['garbanzo'] = 'chickpea'  # just noise, no index for this
        view = getMultiAdapter((portal, req), name='search')
        self.assertIsNone(view.filter_query({'b_start': 0, 'b_size': 10}))
        # resulting empty query, ergo no search performed, empty result:
        self.assertFalse(view.results(batch=False))
        # filter_query() succeeds if 1+ real index name added to request:
        req.form['portal_type'] = 'Document'
        self.assertIsNotNone(view.filter_query({'b_start': 0, 'b_size': 10}))
        res = view.results(batch=False)
        self.assertTrue('my-page1' in [r.getId() for r in res],
                        'Test document is not found in the results.')

    def test_filter_with_plone3_query(self):
        """Filter should ignore obsolete query parameters, not error. """
        portal = self.layer['portal']
        req = test_request()
        # Search.filter_query() will get SearchableText from form if not
        # passed in explicit query argument:
        req.form['SearchableText'] = 'jobs'
        req.form['Title'] = 'Human resource'
        req.form['Description'] = ''
        req.form['created'] = [DateTime('1970/02/01 00:00:00 GMT+0')]
        req.form['created_usage'] = 'range:min'
        req.form['submit'] = 'Search'
        view = getMultiAdapter((portal, req), name='search')
        res = view.results(batch=False)
        self.assertEqual([], [r for r in res])


def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSection))
    return suite
