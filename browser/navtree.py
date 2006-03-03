# This module contains a function to help build navigation-tree-like structures
# from catalog queries. It also contains a standard implementation of the 
# strategy/filtering method that uses Plone's navtree_properties to construct
# navtrees.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_callable, safe_hasattr
from types import StringType

class NavtreeStrategyBase:
    """Base class for navtree strategies.
    """
    
    rootPath = None
    """The path to the root of the navtree (None means use portal root)"""
    
    showAllParents = False
    """Whether or not to show all parents of the current context always"""
    
    def nodeFilter(self, node):
        """Determine whether to include the given node in the tree"""
        return True
        
    def subtreeFilter(self, node):
        """Determine whether to expand the given (folderish) node"""
        return True
        
    def decoratorFactory(self, node):
        """Inject any additional keys in the node that are needed"""
        return node

def buildFolderTree(portal, context=None, query={}, strategy=NavtreeStrategyBase()):
    """Create a tree structure representing a navigation tree. By default,
    it will create a full "sitemap" tree, rooted at the portal, ordered
    by explicit folder order. If the 'query' parameter contains a 'path'
    key, this can be used to override this. To create a navtree rooted
    at the portal root, set query['path'] to:
    
        {'query' : '/'.join(context.getPhysicalPath()),
         'navtree' : 1}
    
    to start this 1 level below the portal root, set query['path'] to:
    
        {'query' : '/'.join(context.getPhysicalPath()),
         'navtree' : 1,
         'navtree_start' : 1}
    
    to create a sitemap with depth limit 3, rooted in the portal:
    
        {'query' : '/'.join(portal.getPhysicalPath()),
         'depth' : 3}
    
    The parameters:
    
    - 'portal' is the portal root, from which tools will be acquired
    - 'context' is the current object being displayed.
    - 'query' is a catalog query to apply to find nodes in the tree.
    - 'strategy' is an object that can affect how the generation works. It
        should be derived from NavtreeStrategyBase, if given, and contain:
        
            rootPath -- a string property; the physical path to the root node.
            
            If not given, it will default to any path set in the query, or the
            portal root. Note that in a navtree query, the root path will 
            default to the portal only, possibly adjusted for any navtree_start
            set. If rootPath points to something not returned by the query by
            the query, a dummy node containing only an empty 'children' list 
            will be returned.
        
            showAllParents -- a boolean property; if true and context is given,
                ensure that all parents of the context, including any that would
                normally be filtered out are included in the tree.
        
            nodeFilter(node) -- a method returning a boolean; if this returns
                False, the given node will not be inserted in the tree
            
            subtreeFilter(node) -- a method returning a boolean; if this returns
                False, the given (folderish) node will not be expanded (its 
                children will be pruned off)
            
            decoratorFactory(node) -- a method returning a dict; this can inject
                additional keys in a node being inserted.
                
    Returns tree where each node is represented by a dict:

        item            -   A catalog brain of this item
        depth           -   The depth of this item, relative to the startAt level
        currentItem     -   True if this is the current item
        currentParent   -   True if this is a direct parent of the current item
        children        -   A list of children nodes of this node
        
    Note: Any 'decoratorFactory' specified may modify this list, but
    the 'children' property is guaranteed to be there. 
    
    Note: If the query does not return the root node itself, the root 
    element of the tree may contain *only* the 'children' list.
    
    Note: Folder default-pages are not included in the returned result. 
    If the 'context' passed in is a default-page, its parent folder will be
    used for the purposes of selecting the 'currentItem'.
    """
    
    portal_url = getToolByName(portal, 'portal_url')
    plone_utils = getToolByName(portal, 'plone_utils')
    portal_catalog = getToolByName(portal, 'portal_catalog')
    
    showAllParents = strategy.showAllParents
    rootPath = strategy.rootPath
    
    # Find the context's path. Use parent folder if context is a default-page
    
    contextPath = None
    if context is not None:
        if plone_utils.isDefaultPage(context):
            contextPath = '/'.join(context.getPhysicalPath()[:-1])
        else:
            contextPath = '/'.join(context.getPhysicalPath())
    
    portalPath = portal_url.getPortalPath()
    
    # Calculate rootPath from the path query if not set. 
    
    if 'path' not in query:
        if rootPath is None:
            rootPath = portalPath
        query['path'] = rootPath
    elif rootPath is None:
        pathQuery = query['path']
        if type(pathQuery) == StringType:
            rootPath = pathQuery
        else:
            # Adjust for the fact that in a 'navtree' query, the actual path
            # is the path of the current context
            if pathQuery.get('navtree', False):
                navtreeLevel = pathQuery.get('navtree_start', 1)
                if navtreeLevel > 1:
                    navtreeContextPath = pathQuery['query']
                    navtreeContextPathElements = navtreeContextPath[len(portalPath)+1:].split('/')
                    # Short-circuit if we won't be able to find this path
                    if len(navtreeContextPathElements) < (navtreeLevel - 1):
                        return {'children' : []}
                    rootPath = portalPath + '/' + '/'.join(navtreeContextPathElements[:navtreeLevel-1])
                else:
                    rootPath = portalPath
            else:
                rootPath = pathQuery['query']
    
    rootDepth = len(rootPath.split('/'))
    
    # Default sorting and threatment of default-pages
    
    if 'sort_on' not in query:
        query['sort_on'] = 'getObjPositionInParent'
    
    if 'is_default_page' not in query:
        query['is_default_page'] = False
    
    results = portal_catalog.searchResults(query)
    
    # We keep track of a dict of item path -> node, so that we can easily
    # find parents and attach children. If a child appears before its 
    # parent, we stub the parent node. 
    
    # This is necessary because whilst the sort_on parameter will ensure 
    # that the objects in a folder are returned in the right order relative
    # to each other, we don't know the relative order of objects from 
    # different folders. So, if /foo comes before /bar, and /foo/a comes
    # before /foo/b, we may get a list like (/bar/x, /foo/a, /foo/b, /foo,
    # /bar,).
    
    itemPaths = {}
    
    def insertElement(itemPaths, item, forceInsert=False):
        """Insert the given 'item' brain into the tree, which is kept in
        'itemPaths'. If 'forceInsert' is True, ignore node- and subtree-
        filters, otherwise any node- or subtree-filter set will be allowed to
        block the insertion of a node.
        """
        itemPath = item.getPath()
        itemInserted = (itemPaths.get(itemPath, {}).get('item', None) is not None)
        
        # Short-circuit if we already added this item. Don't short-circuit
        # if we're forcing the insert, because we may have inserted but
        # later pruned off the node
        if not forceInsert and itemInserted:
            return
        
        itemPhysicalPath = itemPath.split('/')
        parentPath = '/'.join(itemPhysicalPath[:-1])
        parentPruned = (itemPaths.get(parentPath, {}).get('_pruneSubtree', False))
        
        # Short-circuit if we know we're pruning this item's parent
        
        # XXX: We could do this recursively, in case of parent of the
        # parent was being pruned, but this may not be a great trade-off
        
        # There is scope for more efficiency improvement here: If we knew we 
        # were going to prune the subtree, we would short-circuit here each time. 
        # In order to know that, we'd have to make sure we inserted each parent
        # before its children, by sorting the catalog result set (probably
        # manually) to get a breadth-first search.
        
        if not forceInsert and parentPruned:
            return
        
        isCurrent = isCurrentParent = False
        if contextPath is not None:
            if contextPath == itemPath:
                isCurrent = True
            elif contextPath.startswith(itemPath):
                isCurrentParent = True
            
        relativeDepth = len(itemPhysicalPath) - rootDepth
        
        newNode = {'item'          : item,
                   'depth'         : relativeDepth,
                   'currentItem'   : isCurrent,
                   'currentParent' : isCurrentParent,}
            
        insert = True
        if not forceInsert and strategy is not None:
            insert = strategy.nodeFilter(newNode)
        if insert:
            
            if strategy is not None:
                newNode = strategy.decoratorFactory(newNode)
            
            # Tell parent about this item, unless an earlier subtree filter 
            # told us not to. If we're forcing the insert, ignore the
            # pruning, but avoid inserting the node twice
            if itemPaths.has_key(parentPath):
                itemParent = itemPaths[parentPath]
                if forceInsert:
                    nodeAlreadyInserted = False
                    for i in itemParent['children']:
                        if i['item'].getPath() == itemPath:
                            nodeAlreadyInserted = True
                            break
                    if not nodeAlreadyInserted:
                        itemParent['children'].append(newNode)
                elif not itemParent.get('_pruneSubtree', False):
                    itemParent['children'].append(newNode)
            else:
                itemPaths[parentPath] = {'children': [newNode]}
            
            # Ask the subtree filter (if any), if we should be expanding this node
            if strategy.showAllParents and isCurrentParent:
                # If we will be expanding this later, we can't prune off children now
                expand = True
            else:
                expand = getattr(item, 'is_folderish', True)
            if expand and (not forceInsert and strategy is not None):
                expand = strategy.subtreeFilter(newNode)  
            
            if expand:
                # If we had some orphaned children for this node, attach
                # them
                if itemPaths.has_key(itemPath):
                    newNode['children'] = itemPaths[itemPath]['children']
                else:
                    newNode['children'] = []
            else:
                newNode['children'] = []
                newNode['_pruneSubtree'] = True
            
            itemPaths[itemPath] = newNode

    # Add the results of running the query
    for r in results:
        insertElement(itemPaths, r)
    
    # If needed, inject additional nodes for the direct parents of the 
    # context. Note that we use an unrestricted query: things we don't normally
    # have permission to see will be included in the tree.
    if strategy.showAllParents and contextPath is not None:
        contextSubPathElements = contextPath[len(rootPath)+1:].split('/')
        parentPaths = []
        
        haveNode = (itemPaths.get(rootPath, {}).get('item', None) is None)
        if not haveNode:
            parentPaths.append(rootPath)
        
        parentPath = rootPath
        for i in range(len(contextSubPathElements)):
            nodePath = rootPath + '/' + '/'.join(contextSubPathElements[:i+1])
            node = itemPaths.get(nodePath, None)
            
            # If we don't have this node, we'll have to get it, if we have it
            # but it wasn't connected, re-connect it
            if node is None or 'item' not in node:
                parentPaths.append(nodePath)
            else:
                nodeParent = itemPaths.get(parentPath, None)
                if nodeParent is not None:
                    nodeAlreadyInserted = False
                    for i in nodeParent['children']:
                        if i['item'].getPath() == nodePath:
                            nodeAlreadyInserted = True
                            break
                    if not nodeAlreadyInserted:
                        nodeParent['children'].append(node)
                    
            parentPath = nodePath
            
        # If we were outright missing some nodes, find them again
        if len(parentPaths) > 0:
            query = {'path' : {'query' : parentPaths, 'depth' : 0}}
            results = portal_catalog.unrestrictedSearchResults(query)
        
            for r in results:
                insertElement(itemPaths, r, forceInsert=True)
    
    # Return the tree starting at rootPath as the root node. If the
    # root path does not exist, we return a dummy parent node with no children.
    return itemPaths.get(rootPath, {'children' : []})

def getNavigationRoot(portal, context, topLevel=None):
    """Get the path to the root of the navigation tree. If an explicit
    root is set in navtree_properties, use this. If the 'root' property
    is set to an empty string, try to find the root of any virtual host.
    If the property is not set or is set to '/', use the portal root. If
    'topLevel' is given, start this many levels below the given root on
    the path to 'context'. If topLevel is given and context is not below
    the calculated root, return None.
    """
    portal_url = getToolByName(portal, 'portal_url')
    portal_properties = getToolByName(portal, 'portal_properties')
    navtree_properties = getattr(portal_properties, 'navtree_properties')
    
    rootPath = navtree_properties.getProperty('root', None)
    portalPath = portal_url.getPortalPath()
    contextPath = '/'.join(context.getPhysicalPath())
    
    if rootPath:
        if rootPath == '.':
            if context.is_folderish():
                rootPath = '/'.join(context.getPhysicalPath())
            else:
                rootPath = '/'.join(context.getPhysicalPath()[:-1])
        elif rootPath == '/':
            rootPath = portalPath
        else:
            if len(rootPath) > 1 and rootPath[0] == '/':
                rootPath = portalPath + rootPath
            else:
                rootPath = portalPath

    # This code is stolen from Sprout, but it's unclear exactly how it 
    # should work and the test from Sprout isn't directly transferable
    # to testNavTree.py, since it's testing something slightly different.
    # Hoping Sidnei or someone else with a real use case can do this.
    # The idea is that if the 'root' variable is set to '', you'll get
    # the virtual root. This should probably also be used by the default
    # search, as well as the tabs and breadcrumbs. Also, the text in
    # prefs_navigation_form.cpt should be updated if this is re-enabled.
    #
    # Attempt to get use the virtual host root as root if an explicit
    # root is not set
    # if not rootPath:
    #    request = getattr(context, 'REQUEST', None)
    #    if request is not None:
    #        vroot = request.get('VirtualRootPhysicalPath', None)
    #        if vroot is not None:
    #            rootPath = '/'.join(('',) + vroot[len(portalPath):])

    # Fall back on the portal root
    if not rootPath:
        rootPath = portalPath
        
    # Adjust for topLevel
    if topLevel is not None and topLevel > 0:
        if not contextPath.startswith(rootPath):
            return None
        contextSubPathElements = contextPath[len(rootPath)+1:].split('/')
        if len(contextSubPathElements) < topLevel:
            return None
        rootPath = rootPath + '/' + '/'.join(contextSubPathElements[:topLevel])
    
    return rootPath

# Strategy objects for the navtree creation code. You can subclass these
# to expand the default navtree behaviour, and pass instances of your subclasses
# to buildFolderTree().

class NavtreeQueryBuilder:
    """Build a navtree query based on the settings in navtree_properties
    """
    
    def __init__(self, portal, context):
        portal_properties = getToolByName(portal, 'portal_properties')
        portal_url = getToolByName(portal, 'portal_url')
        plone_utils = getToolByName(portal, 'plone_utils')
        
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        
        # Acquire a custom nav query if available
        customQuery = getattr(portal, 'getCustomNavQuery', None)
        if customQuery is not None and safe_callable(customQuery):
            query = customQuery()
        else:
            query = {}

        # Construct the path query
        currentPath = '/'.join(context.getPhysicalPath())
        query['path'] = {'query' : currentPath, 'navtree' : 1}

        topLevel = navtree_properties.getProperty('topLevel', 0)
        if topLevel and topLevel > 0:
             query['path']['navtree_start'] = topLevel + 1

        # XXX: It'd make sense to use 'depth' for bottomLevel, but it doesn't
        # seem to work with EPI.

        # Only list the applicable types
        query['portal_type'] = plone_utils.typesToList()

        # Apply the desired sort
        sortAttribute = navtree_properties.getProperty('sortAttribute', None)
        if sortAttribute is not None:
            query['sort_on'] = sortAttribute
            sortOrder = navtree_properties.getProperty('sortOrder', None)
            if sortOrder is not None:
                query['sort_order'] = sortOrder

        # Filter on workflow states, if enabled
        if navtree_properties.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = navtree_properties.getProperty('wf_states_to_show', ())
        
        self.query = query
        
    def __call__(self):
        return self.query
    
class SitemapQueryBuilder(NavtreeQueryBuilder):
    """Build a folder tree query suitable for a sitemap
    """
    
    def __init__(self, portal, context):
        NavtreeQueryBuilder.__init__(self, portal, context)
        portal_url = getToolByName(portal, 'portal_url')
        portal_properties = getToolByName(portal, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        sitemapDepth = navtree_properties.getProperty('sitemapDepth', 2)
        self.query['path'] = {'query' : portal_url.getPortalPath(),
                              'depth' : sitemapDepth}
        
class SitemapNavtreeStrategy(NavtreeStrategyBase):
    """The navtree building strategy used by the sitemap, based on 
    navtree_properties
    """
    
    def __init__(self, portal, context):
        portal_properties = getToolByName(portal, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        site_properties = getattr(portal_properties, 'site_properties')
        self.excludedIds = {}
        for id in navtree_properties.getProperty('idsNotToList', ()):
            self.excludedIds[id] = True
        self.parentTypesNQ = navtree_properties.getProperty('parentMetaTypesNotToQuery', ())
        self.viewActionTypes = site_properties.getProperty('typesUseViewActionInListings', ())
        self.plone_utils = getToolByName(portal, 'plone_utils')
        
        self.showAllParents = navtree_properties.getProperty('showAllParents', True)
        self.rootPath = getNavigationRoot(portal, context)
        
            
    def nodeFilter(self, node):
        item = node['item']
        if getattr(item, 'getId', None) in self.excludedIds:
            return False
        elif getattr(item, 'exclude_from_nav', False):
            return False
        else:
            return True
        
    def subtreeFilter(self, node):
        portalType = getattr(node['item'], 'portal_type', None)
        if portalType is not None and portalType in self.parentTypesNQ:
            return False
        else:
            return True
    
    def decoratorFactory(self, node):
        newNode = node.copy()
        item = node['item']
        
        portalType = getattr(item, 'portal_type', None)
        itemUrl = item.getURL()
        if portalType is not None and portalType in self.viewActionTypes:
            itemUrl += '/view'
        
        isFolderish = getattr(item, 'is_folderish', None)
        showChildren = False
        if isFolderish and (portalType is None or portalType not in self.parentTypesNQ):
            showChildren = True
        
        newNode['Title'] = self.plone_utils.pretty_title_or_id(item)
        newNode['absolute_url'] = itemUrl
        newNode['getURL'] = itemUrl
        newNode['path'] = item.getPath()
        newNode['icon'] = getattr(item, 'getIcon', None)
        newNode['Creator'] = getattr(item, 'Creator', None)
        newNode['creation_date'] = getattr(item, 'CreationDate', None)
        newNode['portal_type'] = portalType
        newNode['review_state'] = getattr(item, 'review_state', None)
        newNode['Description'] = getattr(item, 'Description', None)
        newNode['getRemoteUrl'] = getattr(item, 'getRemoteUrl', None)
        newNode['show_children'] = showChildren
        newNode['no_display'] = False # We sort this out with the nodeFilter
        
        return newNode

class DefaultNavtreeStrategy(SitemapNavtreeStrategy):
    """The navtree strategy used for the default navigation portlet
    """

    def __init__(self, portal, context):
        SitemapNavtreeStrategy.__init__(self, portal, context)
        portal_properties = getToolByName(portal, 'portal_properties')
        navtree_properties = getattr(portal_properties, 'navtree_properties')
        # XXX: We can't do this with a 'depth' query to EPI...
        self.bottomLevel = navtree_properties.getProperty('bottomLevel', 0)
        topLevel = navtree_properties.getProperty('topLevel', 0)
        self.rootPath = getNavigationRoot(portal, context, topLevel = topLevel)
        
    def subtreeFilter(self, node):
        sitemapDecision = SitemapNavtreeStrategy.subtreeFilter(self, node)
        if sitemapDecision == False:
            return False
        depth = node.get('depth', 0)
        if depth > 0 and self.bottomLevel > 0 and depth >= self.bottomLevel:
            return False
        else:
            return True
    