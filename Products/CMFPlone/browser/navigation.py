from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.Five import BrowserView

from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone.browser.interfaces import INavigationTree
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from Products.CMFPlone.browser.navtree \
    import NavtreeQueryBuilder, SitemapQueryBuilder

from plone.app.layout.navigation.interfaces import INavtreeStrategy

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree


def get_url(item):
    if not item:
        return None
    if hasattr(aq_base(item), 'getURL'):
        # Looks like a brain
        return item.getURL()
    return item.absolute_url()


def get_id(item):
    if not item:
        return None
    getId = getattr(item, 'getId')
    if not utils.safe_callable(getId):
        # Looks like a brain
        return getId
    return getId()


def get_view_url(context):
    props = getToolByName(context, 'portal_properties')
    stp = props.site_properties
    view_action_types = stp.getProperty('typesUseViewActionInListings', ())

    item_url = get_url(context)
    name = get_id(context)

    if hasattr(context, 'portal_type') and context.portal_type in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url


class CatalogNavigationTree(BrowserView):
    implements(INavigationTree)

    def navigationTreeRootPath(self):
        context = aq_inner(self.context)

        portal_properties = getToolByName(context, 'portal_properties')

        navtree_properties = getattr(portal_properties, 'navtree_properties')

        currentFolderOnlyInNavtree = \
            navtree_properties.getProperty('currentFolderOnlyInNavtree', False)
        if currentFolderOnlyInNavtree:
            if context.restrictedTraverse('@@plone').isStructuralFolder():
                return '/'.join(context.getPhysicalPath())
            else:
                return '/'.join(utils.parent(context).getPhysicalPath())

        rootPath = getNavigationRoot(context)

        # Adjust for topLevel
        topLevel = navtree_properties.getProperty('topLevel', None)
        if topLevel is not None and topLevel > 0:
            contextPath = '/'.join(context.getPhysicalPath())
            if not contextPath.startswith(rootPath):
                return None
            contextSubPathElements = contextPath[len(rootPath) + 1:].split('/')
            if len(contextSubPathElements) < topLevel:
                return None
            rootPath = rootPath \
                        + '/' \
                        + '/'.join(contextSubPathElements[:topLevel])

        return rootPath

    def navigationTree(self):
        context = aq_inner(self.context)

        queryBuilder = NavtreeQueryBuilder(context)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context,
                               query=query, strategy=strategy)


class CatalogSiteMap(BrowserView):
    implements(ISiteMap)

    def siteMap(self):
        context = aq_inner(self.context)

        queryBuilder = SitemapQueryBuilder(context)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context,
                               query=query, strategy=strategy)


class CatalogNavigationTabs(BrowserView):
    implements(INavigationTabs)

    def _getNavQuery(self):
        context = self.context
        navtree_properties = self.navtree_properties

        customQuery = getattr(context, 'getCustomNavQuery', False)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        rootPath = getNavigationRoot(context)
        query['path'] = {'query': rootPath, 'depth': 1}

        blacklist = navtree_properties.getProperty('metaTypesNotToList', ())
        all_types = self.portal_catalog.uniqueValuesFor('portal_type')
        query['portal_type'] = [t for t in all_types if t not in blacklist]

        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty(
                                                    'wf_states_to_show', [])

        query['is_default_page'] = False

        if self.site_properties.getProperty('disable_nonfolderish_sections',
                                            False):
            query['is_folderish'] = True

        return query

    def topLevelTabs(self, actions=None, category='portal_tabs'):
        context = aq_inner(self.context)

        mtool = getToolByName(context, 'portal_membership')
        member = mtool.getAuthenticatedMember().id

        portal_properties = getToolByName(context, 'portal_properties')
        self.navtree_properties = getattr(portal_properties,
                                          'navtree_properties')
        self.site_properties = getattr(portal_properties,
                                       'site_properties')
        self.portal_catalog = getToolByName(context, 'portal_catalog')

        if actions is None:
            context_state = getMultiAdapter((context, self.request),
                                            name=u'plone_context_state')
            actions = context_state.actions(category)

        # Build result dict
        result = []
        # first the actions
        if actions is not None:
            for actionInfo in actions:
                data = actionInfo.copy()
                data['name'] = data['title']
                result.append(data)

        # check whether we only want actions
        if self.site_properties.getProperty('disable_folder_sections', False):
            return result

        query = self._getNavQuery()

        rawresult = self.portal_catalog.searchResults(query)

        def get_link_url(item):
            linkremote = item.getRemoteUrl and not member == item.Creator
            if linkremote:
                return (get_id(item), item.getRemoteUrl)
            else:
                return False

        # now add the content to results
        idsNotToList = self.navtree_properties.getProperty('idsNotToList', ())
        for item in rawresult:
            if not (item.getId in idsNotToList or item.exclude_from_nav):
                id, item_url = get_link_url(item) or get_view_url(item)
                data = {'name': utils.pretty_title_or_id(context, item),
                        'id': item.getId,
                        'url': item_url,
                        'description': item.Description}
                result.append(data)

        return result


class CatalogNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        ct = getToolByName(context, 'portal_catalog')
        query = {}

        # Check to see if the current page is a folder default view, if so
        # get breadcrumbs from the parent folder
        if utils.isDefaultPage(context, request):
            currentPath = '/'.join(utils.parent(context).getPhysicalPath())
        else:
            currentPath = '/'.join(context.getPhysicalPath())
        query['path'] = {'query': currentPath, 'navtree': 1, 'depth': 0}

        rawresult = ct(**query)

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

            id, item_url = get_view_url(item)
            data = {'Title': utils.pretty_title_or_id(context, item),
                    'absolute_url': item_url}
            result.append(data)
        return result


class PhysicalNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = aq_inner(self.context)
        request = self.request
        container = utils.parent(context)

        name, item_url = get_view_url(context)

        if container is None:
            return ({'absolute_url': item_url,
                     'Title': utils.pretty_title_or_id(context, context), },
                   )

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation
        # root
        if not utils.isDefaultPage(context, request) \
                and not rootPath.startswith(itemPath):
            base += ({'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context), },
                    )

        return base


class RootPhysicalNavigationBreadcrumbs(BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        # XXX Root never gets included, it's hardcoded as 'Home' in
        # the template. We will fix and remove the hardcoding and fix
        # the tests.
        return ()
