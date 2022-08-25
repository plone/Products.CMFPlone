from Acquisition import aq_base
from Acquisition import aq_inner
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRoot
from plone.base.defaultpage import check_default_page_via_view
from plone.base.interfaces import IHideFromBreadcrumbs
from plone.base.interfaces import INavigationSchema
from plone.base.utils import pretty_title_or_id
from plone.base.utils import safe_callable
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from Products.CMFPlone.utils import parent
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer


def get_url(item):
    if not item:
        return None
    if hasattr(aq_base(item), "getURL"):
        # Looks like a brain
        return item.getURL()
    return item.absolute_url()


def get_id(item):
    if not item:
        return None
    getId = getattr(item, "getId")
    if not safe_callable(getId):
        # Looks like a brain
        return getId
    return getId()


def get_view_url(context):
    registry = getUtility(IRegistry)
    view_action_types = registry.get("plone.types_use_view_action_in_listings", [])
    item_url = get_url(context)
    name = get_id(context)

    if item_url and getattr(context, "portal_type", {}) in view_action_types:
        item_url += "/view"
        name += "/view"

    return name, item_url


@implementer(ISiteMap)
class CatalogSiteMap(BrowserView):
    def siteMap(self):
        context = aq_inner(self.context)

        queryBuilder = SitemapQueryBuilder(context)
        query = queryBuilder()
        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=query, strategy=strategy)


@implementer(INavigationTabs)
class CatalogNavigationTabs(BrowserView):
    def _getNavQuery(self):
        # check whether we only want actions
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(
            INavigationSchema, prefix="plone", check=False
        )
        customQuery = getattr(self.context, "getCustomNavQuery", False)
        if customQuery is not None and safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        query["path"] = {"query": getNavigationRoot(self.context), "depth": 1}
        query["portal_type"] = [t for t in navigation_settings.displayed_types]
        query["sort_on"] = navigation_settings.sort_tabs_on
        if navigation_settings.sort_tabs_reversed:
            query["sort_order"] = "reverse"
        else:
            query["sort_order"] = "ascending"

        if navigation_settings.filter_on_workflow:
            query["review_state"] = navigation_settings.workflow_states_to_show

        query["is_default_page"] = False

        if not navigation_settings.show_excluded_items:
            # Note:
            # Careful with that axe, Eugene!
            # This introduces a performance decrease.
            query["exclude_from_nav"] = False

        if not navigation_settings.nonfolderish_tabs:
            query["is_folderish"] = True

        return query

    def topLevelTabs(self, actions=None, category="portal_tabs"):
        context = aq_inner(self.context)
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(
            INavigationSchema, prefix="plone", check=False
        )
        mtool = getToolByName(context, "portal_membership")
        member = mtool.getAuthenticatedMember().id
        catalog = getToolByName(context, "portal_catalog")

        if actions is None:
            context_state = getMultiAdapter(
                (context, self.request), name="plone_context_state"
            )
            actions = context_state.actions(category)

        # Build result dict
        result = []
        # first the actions
        for actionInfo in actions:
            data = actionInfo.copy()
            data["name"] = data["title"]
            self.customize_entry(data)
            result.append(data)

        # check whether we only want actions
        if not navigation_settings.generate_tabs:
            return result

        query = self._getNavQuery()

        rawresult = catalog.searchResults(query)

        def _get_url(item):
            if item.getRemoteUrl and not member == item.Creator:
                return (get_id(item), item.getRemoteUrl)
            return get_view_url(item)

        context_path = "/".join(context.getPhysicalPath())

        # now add the content to results
        for item in rawresult:
            if item.exclude_from_nav and not context_path.startswith(
                item.getPath()
            ):  # noqa: E501
                # skip excluded items if they're not in our context path
                continue
            cid, item_url = _get_url(item)
            data = {
                "name": pretty_title_or_id(context, item),
                "id": item.getId,
                "url": item_url,
                "description": item.Description,
                "review_state": item.review_state,
            }
            self.customize_entry(data, item)
            result.append(data)

        return result

    def customize_entry(self, entry, brain=None):
        """a little helper to enlarge customizability."""
        pass


@implementer(INavigationBreadcrumbs)
class CatalogNavigationBreadcrumbs(BrowserView):
    def breadcrumbs(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, "portal_catalog")
        query = {}

        # Check to see if the current page is a folder default view, if so
        # get breadcrumbs from the parent folder
        if check_default_page_via_view(context, self.request):
            currentPath = "/".join(parent(context).getPhysicalPath())
        else:
            currentPath = "/".join(context.getPhysicalPath())
        query["path"] = {"query": currentPath, "navtree": 1, "depth": 0}

        rawresult = catalog(**query)

        # Sort items on path length
        dec_result = [(len(r.getPath()), r) for r in rawresult]
        dec_result.sort()

        rootPath = getNavigationRoot(context)

        # Build result dict
        result = []
        for r_tuple in dec_result:
            item = r_tuple[1]

            # Don't include it if it would be above the navigation root
            itemPath = item.getPath()
            if rootPath.startswith(itemPath):
                continue

            cid, item_url = get_view_url(item)
            data = {
                "Title": pretty_title_or_id(context, item),
                "absolute_url": item_url,
            }
            result.append(data)
        return result


@implementer(INavigationBreadcrumbs)
class PhysicalNavigationBreadcrumbs(BrowserView):
    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = parent(context)

        name, item_url = get_view_url(context)

        if container is None:
            return (
                {
                    "absolute_url": item_url,
                    "Title": pretty_title_or_id(context, context),
                },
            )

        view = getMultiAdapter((container, request), name="breadcrumbs_view")
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        rootPath = getNavigationRoot(context)
        itemPath = "/".join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation
        # root
        if not check_default_page_via_view(
            context, request
        ) and not rootPath.startswith(itemPath):
            entry = {
                "absolute_url": item_url,
                "Title": pretty_title_or_id(context, context),
            }
            self.customize_entry(entry, context)
            base += (entry,)
        return base

    def customize_entry(self, entry, context=None):
        """a little helper to enlarge customizability."""
        pass


@implementer(INavigationBreadcrumbs)
class RootPhysicalNavigationBreadcrumbs(BrowserView):
    def breadcrumbs(self):
        # XXX Root never gets included, it's hardcoded as 'Home' in
        # the template. We will fix and remove the hardcoding and fix
        # the tests.
        return ()
