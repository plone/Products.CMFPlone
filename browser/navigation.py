from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getUtility

from Acquisition import aq_base
from Products.CMFPlone import utils

from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import IURLTool

from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone.browser.interfaces import INavigationTree
from Products.CMFPlone.browser.interfaces import ISiteMap
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder, SitemapQueryBuilder

# Nasty hack to circumvent 'plone' modulealias
import sys
import plone
del sys.modules['Products.CMFPlone.browser.plone']

from plone.app.layout.navigation.interfaces import INavtreeStrategy

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.navtree import buildFolderTree

from plone.memoize.view import memoize_contextless

import zope.deferredimport
zope.deferredimport.deprecated(
    "It has been moved to plone.app.layout.navigation.defaultpage. " 
    "This alias will be removed in Plone 4.0",
    DefaultPage = 'plone.app.layout.navigation.defaultpage:DefaultPage',
    )
    
import ploneview
sys.modules['Products.CMFPlone.browser.plone'] = ploneview

def get_url(item):
    if hasattr(aq_base(item), 'getURL'):
        # Looks like a brain
        return item.getURL()
    return item.absolute_url()

def get_id(item):
    getId = getattr(item, 'getId')
    if not utils.safe_callable(getId):
        # Looks like a brain
        return getId
    return getId()

def get_view_url(context):
    props = getUtility(IPropertiesTool)
    stp = props.site_properties
    view_action_types = stp.getProperty('typesUseViewActionInListings', ())

    item_url = get_url(context)
    name = get_id(context)

    if context.portal_type in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url

class CatalogNavigationTree(utils.BrowserView):
    implements(INavigationTree)

    def navigationTreeRootPath(self):
        context = utils.context(self)

        portal_properties = getUtility(IPropertiesTool)
        portal_url = getUtility(IURLTool)

        navtree_properties = getattr(portal_properties, 'navtree_properties')

        currentFolderOnlyInNavtree = navtree_properties.getProperty('currentFolderOnlyInNavtree', False)
        if currentFolderOnlyInNavtree:
            if context.is_folderish():
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
            contextSubPathElements = contextPath[len(rootPath)+1:].split('/')
            if len(contextSubPathElements) < topLevel:
                return None
            rootPath = rootPath + '/' + '/'.join(contextSubPathElements[:topLevel])

        return rootPath

    def navigationTree(self):
        context = utils.context(self)

        queryBuilder = NavtreeQueryBuilder(context)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=query, strategy=strategy)

class CatalogSiteMap(utils.BrowserView):
    implements(ISiteMap)

    def siteMap(self):
        context = utils.context(self)

        queryBuilder = SitemapQueryBuilder(context)
        query = queryBuilder()

        strategy = getMultiAdapter((context, self), INavtreeStrategy)

        return buildFolderTree(context, obj=context, query=query, strategy=strategy)


class CatalogNavigationTabs(utils.BrowserView):
    implements(INavigationTabs)

    @memoize_contextless
    def topLevelTabs(self, actions=None, category='portal_tabs'):
        context = utils.context(self)

        portal_properties = getUtility(IPropertiesTool)
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')

        # Build result dict
        result = []
        # first the actions
        if actions is None:
            actions_tool = getUtility(IActionsTool)
            actions = (actions_tool.listActionInfos(object=context,
                                                    categories=(category, )))
            for action in actions:
                action['name'] = action['title']
        result.extend(actions)

        # check whether we only want actions
        if site_properties.getProperty('disable_folder_sections', False):
            return result

        portal_catalog = getUtility(ICatalogTool)
        customQuery = getattr(context, 'getCustomNavQuery', False)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        rootPath = getNavigationRoot(context)
        query['path'] = {'query' : rootPath, 'depth' : 1}

        query['portal_type'] = utils.typesToList(context)

        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute

            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', [])

        query['is_default_page'] = False
        query['is_folderish'] = True

        # Get ids not to list and make a dict to make the search fast
        idsNotToList = navtree_properties.getProperty('idsNotToList', ())
        excludedIds = {}
        for id in idsNotToList:
            excludedIds[id]=1

        rawresult = portal_catalog.searchResults(query)

        # now add the content to results
        for item in rawresult:
            if not (excludedIds.has_key(item.getId) or item.exclude_from_nav):
                id, item_url = get_view_url(item)
                data = {'name'      : utils.pretty_title_or_id(context, item),
                        'id'         : id,
                        'url'        : item_url,
                        'description': item.Description}
                result.append(data)
        return result


class CatalogNavigationBreadcrumbs(utils.BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = utils.context(self)
        request = self.request
        ct = getUtility(ICatalogTool)
        query = {}

        # Check to see if the current page is a folder default view, if so
        # get breadcrumbs from the parent folder
        if utils.isDefaultPage(context, request):
            currentPath = '/'.join(utils.parent(context).getPhysicalPath())
        else:
            currentPath = '/'.join(context.getPhysicalPath())
        query['path'] = {'query':currentPath, 'navtree':1, 'depth': 0}

        rawresult = ct(**query)

        # Sort items on path length
        dec_result = [(len(r.getPath()),r) for r in rawresult]
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


class PhysicalNavigationBreadcrumbs(utils.BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = utils.context(self)
        request = self.request
        container = utils.parent(context)

        try:
            name, item_url = get_view_url(context)
        except AttributeError:
            print context
            raise

        if container is None:
            return ({'absolute_url': item_url,
                     'Title': utils.pretty_title_or_id(context, context),
                    },)

        view = getMultiAdapter((container, request), name='breadcrumbs_view')
        base = tuple(view.breadcrumbs())

        # Some things want to be hidden from the breadcrumbs
        if IHideFromBreadcrumbs.providedBy(context):
            return base

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        rootPath = getNavigationRoot(context)
        itemPath = '/'.join(context.getPhysicalPath())

        # don't show default pages in breadcrumbs or pages above the navigation root
        if not utils.isDefaultPage(context, request) and not rootPath.startswith(itemPath):
            base += ({'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context),
                     },)

        return base


class RootPhysicalNavigationBreadcrumbs(utils.BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        # XXX Root never gets included, it's hardcoded as 'Home' in
        # the template. We will fix and remove the hardcoding and fix
        # the tests.
        context = utils.context(self)
        return ()
