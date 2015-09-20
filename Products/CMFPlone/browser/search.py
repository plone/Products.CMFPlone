# -*- coding: utf-8 -*-

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.ZCTextIndex.ParseTree import ParseError
from ZTUtils import make_query
from plone.app.contentlisting.interfaces import IContentListing
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.publisher.browser import BrowserView

import json

_ = MessageFactory('plone')

# We should accept both a simple space, unicode u'\u0020 but also a
# multi-space, so called 'waji-kankaku', unicode u'\u3000'
MULTISPACE = u'\u3000'.encode('utf-8')
BAD_CHARS = ('?', '-', '+', '*', MULTISPACE)
EVER = DateTime('1970-01-03')


def quote_chars(s):
    # We need to quote parentheses when searching text indices
    if '(' in s:
        s = s.replace('(', '"("')
    if ')' in s:
        s = s.replace(')', '")"')
    if MULTISPACE in s:
        s = s.replace(MULTISPACE, ' ')
    return s


class Search(BrowserView):

    valid_keys = ('sort_on', 'sort_order', 'sort_limit', 'fq', 'fl', 'facet')

    def munge_search_term(self, q):
        for char in BAD_CHARS:
            q = q.replace(char, ' ')
        r = q.split()
        r = " AND ".join(r)
        r = quote_chars(r) + '*'
        return r

    def results(self, query=None, batch=True, b_size=10, b_start=0,
                use_content_listing=True):
        """ Get properly wrapped search results from the catalog.
        Everything in Plone that performs searches should go through this view.
        'query' should be a dictionary of catalog parameters.
        """
        if query is None:
            query = {}
        if batch:
            query['b_start'] = b_start = int(b_start)
            query['b_size'] = b_size
        query = self.filter_query(query)

        if query is None:
            results = []
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            try:
                results = catalog(**query)
            except ParseError:
                return []

        if use_content_listing:
            results = IContentListing(results)
        if batch:
            results = Batch(results, b_size, b_start)
        return results

    def filter_query(self, query):
        request = self.request

        catalog = getToolByName(self.context, 'portal_catalog')
        valid_indexes = tuple(catalog.indexes())
        valid_keys = self.valid_keys + valid_indexes

        text = query.get('SearchableText', None)
        if text is None:
            text = request.form.get('SearchableText', '')
        if not text:
            # Without text, must provide a meaningful non-empty search
            valid = set(valid_indexes).intersection(request.form.keys()) or \
                set(valid_indexes).intersection(query.keys())
            if not valid:
                return

        for k, v in request.form.items():
            if v and ((k in valid_keys) or k.startswith('facet.')):
                query[k] = v
        if text:
            query['SearchableText'] = self.munge_search_term(text)

        # don't filter on created at all if we want all results
        created = query.get('created')
        if created:
            try:
                if created.get('query') and created['query'][0] <= EVER:
                    del query['created']
            except AttributeError:
                # created not a mapping
                del query['created']

        # respect `types_not_searched` setting
        types = query.get('portal_type', [])
        if 'query' in types:
            types = types['query']
        query['portal_type'] = self.filter_types(types)
        # respect effective/expiration date
        query['show_inactive'] = False
        # respect navigation root
        if 'path' not in query:
            query['path'] = getNavigationRoot(self.context)

        if 'sort_order' in query and not query['sort_order']:
            del query['sort_order']
        return query

    def filter_types(self, types):
        plone_utils = getToolByName(self.context, 'plone_utils')
        if not isinstance(types, list):
            types = [types]
        return plone_utils.getUserFriendlyTypes(types)

    def types_list(self):
        # only show those types that have any content
        catalog = getToolByName(self.context, 'portal_catalog')
        used_types = catalog._catalog.getIndex('portal_type').uniqueValues()
        return self.filter_types(list(used_types))

    def sort_options(self):
        """ Sorting options for search results view. """
        return (
            SortOption(self.request, _(u'relevance'), ''),
            SortOption(
                self.request, _(u'date (newest first)'),
                'Date', reverse=True
            ),
            SortOption(self.request, _(u'alphabetically'), 'sortable_title'),
        )

    def show_advanced_search(self):
        """Whether we need to show advanced search options a.k.a. filters?"""
        show = self.request.get('advanced_search', None)
        if not show or show == 'False':
            return False
        return True

    def advanced_search_trigger(self):
        """URL builder for show/close advanced search filters."""
        query = self.request.get('QUERY_STRING', None)
        url = self.request.get('ACTUAL_URL', self.context.absolute_url())
        if not query:
            return url
        if 'advanced_search' in query:
            if 'advanced_search=True' in query:
                query = query.replace('advanced_search=True', '')
            if 'advanced_search=False' in query:
                query = query.replace('advanced_search=False', '')
        else:
            query = query + '&advanced_search=True'
        return url + '?' + query

    def breadcrumbs(self, item):
        obj = item.getObject()
        view = getMultiAdapter((obj, self.request), name='breadcrumbs_view')
        # cut off the item itself
        breadcrumbs = list(view.breadcrumbs())[:-1]
        if len(breadcrumbs) == 0:
            # don't show breadcrumbs if we only have a single element
            return None
        if len(breadcrumbs) > 3:
            # if we have too long breadcrumbs, emit the middle elements
            empty = {'absolute_url': '', 'Title': unicode('…', 'utf-8')}
            breadcrumbs = [breadcrumbs[0], empty] + breadcrumbs[-2:]
        return breadcrumbs

    def navroot_url(self):
        if not hasattr(self, '_navroot_url'):
            state = self.context.unrestrictedTraverse('@@plone_portal_state')
            self._navroot_url = state.navigation_root_url()
        return self._navroot_url


class AjaxSearch(Search):

    def __call__(self):
        items = []
        try:
            per_page = int(self.request.form.get('perPage'))
        except:
            per_page = 10
        try:
            page = int(self.request.form.get('page'))
        except:
            page = 1

        results = self.results(batch=False, use_content_listing=False)
        batch = Batch(results, per_page, start=(page - 1) * per_page)

        registry = queryUtility(IRegistry)
        length = registry.get('plone.search_results_description_length')
        plone_view = getMultiAdapter(
            (self.context, self.request), name='plone')
        registry = getUtility(IRegistry)
        view_action_types = registry.get(
            'plone.types_use_view_action_in_listings', [])
        for item in batch:
            url = item.getURL()
            if item.portal_type in view_action_types:
                url = '%s/view' % url
            items.append({
                'id': item.UID,
                'title': item.Title,
                'description': plone_view.cropText(item.Description, length),
                'url': url,
                'state': item.review_state if item.review_state else None,
            })
        return json.dumps({
            'total': len(results),
            'items': items
        })


class SortOption(object):

    def __init__(self, request, title, sortkey='', reverse=False):
        self.request = request
        self.title = title
        self.sortkey = sortkey
        self.reverse = reverse

    def selected(self):
        sort_on = self.request.get('sort_on', '')
        return sort_on == self.sortkey

    def url(self):
        q = {}
        q.update(self.request.form)
        if 'sort_on' in q.keys():
            del q['sort_on']
        if 'sort_order' in q.keys():
            del q['sort_order']
        q['sort_on'] = self.sortkey
        if self.reverse:
            q['sort_order'] = 'reverse'

        base_url = self.request.URL
        return base_url + '?' + make_query(q)
