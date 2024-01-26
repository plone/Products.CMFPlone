from DateTime import DateTime
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.base.batch import Batch
from plone.base.interfaces import ISearchSchema
from plone.base.interfaces.siteroot import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.ZCTextIndex.ParseTree import ParseError
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18nmessageid import MessageFactory
from zope.publisher.browser import BrowserView
from ZTUtils import make_query

import json
import re


_ = MessageFactory("plone")

# We should accept both a simple space, unicode u'\u0020 but also a
# multi-space, so called 'waji-kankaku', unicode u'\u3000'
MULTISPACE = "\u3000"
BAD_CHARS = ("?", "-", "+", "*", MULTISPACE)
EVER = DateTime("1970-01-03")


def quote_chars(s):
    # We need to quote parentheses when searching text indices
    if "(" in s:
        s = s.replace("(", '"("')
    if ")" in s:
        s = s.replace(")", '")"')
    if MULTISPACE in s:
        s = s.replace(MULTISPACE, " ")
    return s


def quote(term):
    # The terms and, or and not must be wrapped in quotes to avoid
    # being parsed as logical query atoms.
    if term.lower() in ("and", "or", "not"):
        term = '"%s"' % term
    return quote_chars(term)


def munge_search_term(query):
    original_query = query
    for char in BAD_CHARS:
        query = query.replace(char, " ")

    # extract quoted phrases first
    quoted_phrases = re.findall(r'"([^"]*)"', query)
    r = []
    for qp in quoted_phrases:
        # remove from original query
        query = query.replace(f'"{qp}"', "")
        # replace with cleaned leading/trailing whitespaces
        # and skip empty phrases
        clean_qp = qp.strip()
        if not clean_qp:
            continue
        r.append(f'"{clean_qp}"')

    r += map(quote, query.strip().split())
    r = " AND ".join(r)
    r = r + ("*" if r and not original_query.endswith('"') else "")
    return r


class Search(BrowserView):
    valid_keys = ("sort_on", "sort_order", "sort_limit", "fq", "fl", "facet")

    def results(
        self, query=None, batch=True, b_size=10, b_start=0, use_content_listing=True
    ):
        """Get properly wrapped search results from the catalog.
        Everything in Plone that performs searches should go through this view.
        'query' should be a dictionary of catalog parameters.
        """
        if query is None:
            query = {}
        if batch:
            query["b_start"] = b_start = int(b_start)
            query["b_size"] = b_size
        query = self.filter_query(query)

        if query is None:
            results = []
        else:
            catalog = getToolByName(self.context, "portal_catalog")
            try:
                results = catalog(**query)
            except ParseError:
                return []

        if use_content_listing:
            results = IContentListing(results)
        if batch:
            results = Batch(results, b_size, b_start)
        return results

    def _filter_query(self, query):
        request = self.request

        catalog = getToolByName(self.context, "portal_catalog")
        valid_indexes = tuple(catalog.indexes())
        valid_keys = self.valid_keys + valid_indexes

        text = query.get("SearchableText", None)
        if text is None:
            text = request.form.get("SearchableText", "")
        if not text:
            # Without text, must provide a meaningful non-empty search
            valid = set(valid_indexes).intersection(request.form.keys()) or set(
                valid_indexes
            ).intersection(query.keys())
            if not valid:
                return

        for k, v in request.form.items():
            if v and ((k in valid_keys) or k.startswith("facet.")):
                query[k] = v
        if text:
            query["SearchableText"] = munge_search_term(text)

        # don't filter on created at all if we want all results
        created = query.get("created")
        if created:
            try:
                if created.get("query", EVER) <= EVER:
                    del query["created"]
            except AttributeError:
                # created not a mapping
                del query["created"]

        # respect `types_not_searched` setting
        types = query.get("portal_type", [])
        if "query" in types:
            types = types["query"]
        query["portal_type"] = self.filter_types(types)
        # respect effective/expiration date
        query["show_inactive"] = False
        # respect navigation root if we're not at the site root.
        if "path" not in query and not IPloneSiteRoot.providedBy(self.context):
            query["path"] = getNavigationRoot(self.context)

        if "sort_order" in query and not query["sort_order"]:
            del query["sort_order"]
        return query

    @lazy_property
    def default_sort_on(self):
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        return search_settings.sort_on

    def filter_query(self, query):
        query = self._filter_query(query)
        if query is None:
            query = {}
        # explicitly set a sort; if no `sort_on` is present, the catalog sorts
        # by relevance
        if "sort_on" not in query:
            self.default_sort_on
            if self.default_sort_on != "relevance":
                query["sort_on"] = self.default_sort_on
        elif query["sort_on"] == "relevance":
            del query["sort_on"]
        if query.get("sort_on", "") == "Date":
            query["sort_order"] = "reverse"
        elif "sort_order" in query:
            del query["sort_order"]
        if not query:
            return None
        return query

    def filter_types(self, types):
        plone_utils = getToolByName(self.context, "plone_utils")
        if not isinstance(types, list):
            types = [types]
        return plone_utils.getUserFriendlyTypes(types)

    def types_list(self):
        # only show those types that have any content
        catalog = getToolByName(self.context, "portal_catalog")
        used_types = catalog._catalog.getIndex("portal_type").uniqueValues()
        return self.filter_types(list(used_types))

    def sort_options(self):
        """Sorting options for search results view."""
        if "sort_on" not in self.request.form:
            self.request.form["sort_on"] = self.default_sort_on
        return (
            SortOption(self.request, _("relevance"), "relevance"),
            SortOption(self.request, _("date (newest first)"), "Date", reverse=True),
            SortOption(self.request, _("alphabetically"), "sortable_title"),
        )

    def show_advanced_search(self):
        """Whether we need to show advanced search options a.k.a. filters?"""
        show = self.request.get("advanced_search", None)
        if not show or show == "False":
            return False
        return True

    def advanced_search_trigger(self):
        """URL builder for show/close advanced search filters."""
        query = self.request.get("QUERY_STRING", None)
        url = self.request.get("ACTUAL_URL", self.context.absolute_url())
        if not query:
            return url
        if "advanced_search" in query:
            if "advanced_search=True" in query:
                query = query.replace("advanced_search=True", "")
            if "advanced_search=False" in query:
                query = query.replace("advanced_search=False", "")
        else:
            query = query + "&advanced_search=True"
        return url + "?" + query

    def breadcrumbs(self, item):
        obj = item.getObject()
        view = getMultiAdapter((obj, self.request), name="breadcrumbs_view")
        # cut off the item itself
        breadcrumbs = list(view.breadcrumbs())[:-1]
        if len(breadcrumbs) == 0:
            # don't show breadcrumbs if we only have a single element
            return None
        if len(breadcrumbs) > 3:
            # if we have too long breadcrumbs, emit the middle elements
            empty = {"absolute_url": "", "Title": "…"}
            breadcrumbs = [breadcrumbs[0], empty] + breadcrumbs[-2:]
        return breadcrumbs

    def navroot_url(self):
        if not hasattr(self, "_navroot_url"):
            state = self.context.unrestrictedTraverse("@@plone_portal_state")
            self._navroot_url = state.navigation_root_url()
        return self._navroot_url

    @property
    def show_images(self):
        registry = queryUtility(IRegistry)
        return registry.get("plone.search_show_images")

    @property
    def search_image_scale(self):
        registry = queryUtility(IRegistry)
        return registry.get("plone.search_image_scale")


class AjaxSearch(Search):
    def __call__(self):
        items = []
        try:
            per_page = int(self.request.form.get("perPage"))
        except Exception:
            per_page = 10
        try:
            page = int(self.request.form.get("page"))
        except Exception:
            page = 1

        results = self.results(batch=False, use_content_listing=False)
        batch = Batch(results, per_page, start=(page - 1) * per_page)

        registry = queryUtility(IRegistry)
        length = registry.get("plone.search_results_description_length")
        show_images = registry.get("plone.search_show_images")
        if show_images:
            image_scale = registry.get("plone.search_image_scale")
            # image_scaling = getMultiAdapter((self.context, self.request), name='image_scale')
            self.image_scaling = getMultiAdapter(
                (INavigationRoot(self.context), self.request), name="image_scale"
            )
        plone_view = getMultiAdapter((self.context, self.request), name="plone")
        view_action_types = registry.get("plone.types_use_view_action_in_listings", [])
        for item in batch:
            url = item.getURL()
            if item.portal_type in view_action_types:
                url = "%s/view" % url
            img_tag = None
            if show_images:
                img_tag = self.get_image_tag(item, image_scale)
            items.append(
                {
                    "id": item.UID,
                    "title": item.Title,
                    "description": plone_view.cropText(item.Description, length),
                    "url": url,
                    "state": item.review_state if item.review_state else None,
                    "img_tag": img_tag,
                }
            )
        return json.dumps({"total": len(results), "items": items})

    def get_image_tag(self, item, image_scale):
        return self.image_scaling.tag(item, "image", scale=image_scale)


class SortOption:
    def __init__(self, request, title, sortkey="", reverse=False):
        self.request = request
        self.title = title
        self.sortkey = sortkey
        self.reverse = reverse

    def selected(self):
        sort_on = self.request.get("sort_on", "")
        return sort_on == self.sortkey and sort_on != ""

    def url(self):
        q = {}
        q.update(self.request.form)
        if "sort_on" in q.keys():
            del q["sort_on"]
        if "sort_order" in q.keys():
            del q["sort_order"]
        q["sort_on"] = self.sortkey
        if self.reverse:
            q["sort_order"] = "reverse"

        base_url = self.request.URL
        return base_url + "?" + make_query(q)
