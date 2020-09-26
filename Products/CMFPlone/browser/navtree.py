# This module contains a function to help build navigation-tree-like structures
# from catalog queries. It also contains a standard implementation of the
# strategy/filtering method that uses Plone's navtree_properties to construct
# navtrees.
from AccessControl import ModuleSecurityInfo
from Acquisition import aq_inner
from plone.app.layout.navigation.interfaces import INavigationQueryBuilder
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import NavtreeStrategyBase
from plone.app.layout.navigation.root import getNavigationRoot
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.interfaces import INavigationSchema
from zope.component import getMultiAdapter, queryUtility
from zope.component import getUtility
from zope.interface import implementer

# Strategy objects for the navtree creation code. You can subclass these
# to expand the default navtree behaviour, and pass instances of your
# subclasses to buildFolderTree().

security = ModuleSecurityInfo()
security.declarePrivate('plone')
security.declarePrivate('utils')


@implementer(INavigationQueryBuilder)
class NavtreeQueryBuilder:
    """Build a navtree query based on the settings in navtree_properties
    """

    def __init__(self, context):
        registry = getUtility(IRegistry)
        navigation_settings = registry.forInterface(INavigationSchema,
                                                    prefix="plone")

        # Acquire a custom nav query if available
        customQuery = getattr(context, 'getCustomNavQuery', None)
        if customQuery is not None and utils.safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        # Construct the path query

        rootPath = getNavigationRoot(context)
        currentPath = '/'.join(context.getPhysicalPath())

        # If we are above the navigation root, a navtree query would return
        # nothing (since we explicitly start from the root always). Hence,
        # use a regular depth-1 query in this case.

        if not currentPath.startswith(rootPath):
            query['path'] = {'query': rootPath, 'depth': 1}
        else:
            query['path'] = {'query': currentPath, 'navtree': 1}

        query['path']['navtree_start'] = 0

        # XXX: It'd make sense to use 'depth' for bottomLevel, but it doesn't
        # seem to work with EPI.

        # Only list the applicable types
        query['portal_type'] = utils.typesToList(context)

        # Apply the desired sort
        sortAttribute = navigation_settings.sort_tabs_on
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            if navigation_settings.sort_tabs_reversed:
                query['sort_order'] = 'desc'
            else:
                query['sort_order'] = 'asc'

        # Filter on workflow states, if enabled
        if navigation_settings.filter_on_workflow:
            query['review_state'] = navigation_settings.workflow_states_to_show

        self.query = query

    def __call__(self):
        return self.query


class SitemapQueryBuilder(NavtreeQueryBuilder):
    """Build a folder tree query suitable for a sitemap
    """

    def __init__(self, context):
        NavtreeQueryBuilder.__init__(self, context)
        portal_url = getToolByName(context, 'portal_url')
        registry = getUtility(IRegistry)
        sitemap_depth = registry.get('plone.sitemap_depth', 3)
        self.query['path'] = {'query': portal_url.getPortalPath(),
                              'depth': sitemap_depth}


@implementer(INavtreeStrategy)
class SitemapNavtreeStrategy(NavtreeStrategyBase):
    """The navtree building strategy used by the sitemap, based on
    navtree_properties
    """

    def __init__(self, context, view=None):
        self.context = context

        portal_url = getToolByName(context, 'portal_url')
        self.portal = portal_url.getPortalObject()
        registry = getUtility(IRegistry)
        self.parentTypesNQ = registry.get(
            'plone.parent_types_not_to_query', [])
        self.viewActionTypes = registry.get(
            'plone.types_use_view_action_in_listings', [])

        self.showAllParents = True
        self.rootPath = getNavigationRoot(context)

        membership = getToolByName(context, 'portal_membership')
        self.memberId = membership.getAuthenticatedMember().getId()

    def nodeFilter(self, node):
        return not getattr(node['item'], 'exclude_from_nav', False)

    def subtreeFilter(self, node):
        portalType = getattr(node['item'], 'portal_type', None)
        return portalType is None or portalType not in self.parentTypesNQ

    def decoratorFactory(self, node):
        context = aq_inner(self.context)
        request = context.REQUEST

        newNode = node.copy()
        item = node['item']

        portalType = getattr(item, 'portal_type', None)
        itemUrl = item.getURL()
        if portalType is not None and portalType in self.viewActionTypes:
            itemUrl += '/view'

        useRemoteUrl = False
        getRemoteUrl = getattr(item, 'getRemoteUrl', None)
        isCreator = self.memberId == getattr(item, 'Creator', None)
        if getRemoteUrl and not isCreator:
            useRemoteUrl = True

        isFolderish = getattr(item, 'is_folderish', None)
        showChildren = False
        if isFolderish and \
                (portalType is None or portalType not in self.parentTypesNQ):
            showChildren = True

        layout_view = getMultiAdapter((context, request), name='plone_layout')

        newNode['Title'] = utils.pretty_title_or_id(context, item)
        newNode['id'] = item.getId
        newNode['UID'] = item.UID
        newNode['absolute_url'] = itemUrl
        newNode['getURL'] = itemUrl
        newNode['path'] = item.getPath()
        newNode['Creator'] = getattr(item, 'Creator', None)
        newNode['creation_date'] = getattr(item, 'CreationDate', None)
        newNode['portal_type'] = portalType
        newNode['review_state'] = getattr(item, 'review_state', None)
        newNode['Description'] = getattr(item, 'Description', None)
        newNode['show_children'] = showChildren
        newNode['no_display'] = False  # We sort this out with the nodeFilter
        # BBB getRemoteUrl and link_remote are deprecated, remove in Plone 4
        newNode['getRemoteUrl'] = getattr(item, 'getRemoteUrl', None)
        newNode['useRemoteUrl'] = useRemoteUrl
        newNode['link_remote'] = (
            newNode['getRemoteUrl'] and newNode['Creator'] != self.memberId
        )

        idnormalizer = queryUtility(IIDNormalizer)
        newNode['normalized_portal_type'] = idnormalizer.normalize(portalType)
        newNode['normalized_review_state'] = idnormalizer.normalize(
            newNode['review_state']
        )
        newNode['normalized_id'] = idnormalizer.normalize(newNode['id'])

        return newNode

    def showChildrenOf(self, object):
        getTypeInfo = getattr(object, 'getTypeInfo', None)
        if getTypeInfo is not None:
            portal_type = getTypeInfo().getId()
            if portal_type in self.parentTypesNQ:
                return False
        return True


@implementer(INavtreeStrategy)
class DefaultNavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the default navigation portlet
    """

    def __init__(self, context, view=None):
        SitemapNavtreeStrategy.__init__(self, context, view)
        if view is not None:
            self.rootPath = view.navigationTreeRootPath()
        else:
            self.rootPath = getNavigationRoot(context)

    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)
        if not sitemapDecision:
            return False
        depth = node.get('depth', 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        return True
