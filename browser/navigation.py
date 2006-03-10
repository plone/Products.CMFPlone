from zope.interface import implements
from zope.component import getView

from Acquisition import aq_base, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.browser.interfaces import IDefaultPage
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.interfaces import INavigationTabs
from Products.CMFPlone.browser.interfaces import INavigationTree
from Products.CMFPlone.browser.interfaces import INavigationStructure
from Products.CMFPlone.interfaces.BrowserDefault import IBrowserDefault
from Products.CMFPlone.interfaces.BrowserDefault import IDynamicViewTypeInformation

from Products.CMFPlone.browser.navtree import buildFolderTree
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder, SitemapQueryBuilder

# XXX: Should move these to use multi-adapters on the INavtreeStrategy interface
from Products.CMFPlone.browser.navtree import DefaultNavtreeStrategy, SitemapNavtreeStrategy

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
    props = getToolByName(context, 'portal_properties')
    stp = props.site_properties
    view_action_types = stp.getProperty('typesUseViewActionInListings', ())

    item_url = get_url(context)
    name = get_id(context)

    if context.portal_type in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url

class DefaultPage(utils.BrowserView):
    implements(IDefaultPage)

    def isDefaultPage(self, obj, context_=None):
        """Finds out if the given obj is the default page in its parent folder.

        Only considers explicitly contained objects, either set as index_html,
        with the default_page property, or using IBrowserDefault.
        """
        #XXX: What is this context/obj confusion all about?
        if context_ is None:
            context_ = obj
        parentDefaultPage = self.getDefaultPage(context_)
        if parentDefaultPage is None or '/' in parentDefaultPage:
            return False
        return (parentDefaultPage == obj.getId())

    def getDefaultPage(self, context_=None):
        """Given a folderish item, find out if it has a default-page using
        the following lookup rules:

            1. A content object called 'index_html' wins
            2. If the folder implements IBrowserDefault, query this
            3. Else, look up the property default_page on the object
                - Note that in this case, the returned id may *not* be of an
                  object in the folder, since it could be acquired from a
                  parent folder or skin layer
            4. Else, look up the property default_page in site_properties for
                magic ids and test these

        The id of the first matching item is then used to lookup a translation
        and if found, its id is returned. If no default page is set, None is
        returned. If a non-folderish item is passed in, return None always.
        """
        context = utils.context(self)
        if context_ is None:
            context_ = context

        # The list of ids where we look for default
        ids = {}

        # For BTreeFolders we just use the has_key, otherwise build a dict
        if hasattr(aq_base(context), 'has_key'):
            ids = context
        else:
            for id in context.objectIds():
                ids[id] = 1

        # Inline function with default argument.
        def lookupTranslationId(obj, page):
            return utils.lookupTranslationId(obj, page, ids)

        # 1. test for contentish index_html
        if ids.has_key('index_html'):
            return lookupTranslationId(context, 'index_html')

        # 2. Test for IBrowserDefault
        if IBrowserDefault.isImplementedBy(context):
            fti = context.getTypeInfo()
            if fti is not None:
                # Also check that the fti is really IDynamicViewTypeInformation
                if IDynamicViewTypeInformation.isImplementedBy(fti):
                    page = fti.getDefaultPage(context, check_exists=True)
                    if page is not None:
                        return lookupTranslationId(context, page)

        # 3. Test for default_page property in folder, then skins
        pages = getattr(aq_base(context), 'default_page', [])
        if isinstance(pages, basestring):
            pages = [pages]
        for page in pages:
            if page and ids.has_key(page):
                return lookupTranslationId(context, page)

        portal = getToolByName(context_, 'portal_url').getPortalObject()
        for page in pages:
            if portal.unrestrictedTraverse(page, None):
                return lookupTranslationId(context, page)

        # 4. Test for default sitewide default_page setting
        site_properties = portal.portal_properties.site_properties
        for page in site_properties.getProperty('default_page', []):
            if ids.has_key(page):
                return lookupTranslationId(context, page)

        return None

class CatalogNavigationTree(utils.BrowserView):
    implements(INavigationTree)

    def navigationTree(self):
        context = utils.context(self)
        
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        
        # XXX: Should use muliti-adapter lookups to get strategies
        
        queryBuilder = NavtreeQueryBuilder(portal, context)
        strategy = DefaultNavtreeStrategy(portal, context)
        
        query = queryBuilder()
        
        return buildFolderTree(portal, context=context, query=query, strategy=strategy)

    def siteMap(self):
        context = utils.context(self)
        
        portal_url = getToolByName(context, 'portal_url')
        portal = portal_url.getPortalObject()
        
        # XXX: Should use muliti-adapter lookups to get strategies
        
        queryBuilder = SitemapQueryBuilder(portal, context)
        strategy = SitemapNavtreeStrategy(portal, context)
        
        query = queryBuilder()
        
        return buildFolderTree(portal, context=context, query=query, strategy=strategy)

class CatalogNavigationTabs(utils.BrowserView):
    implements(INavigationTabs)

    def topLevelTabs(self, actions=None):
        context = utils.context(self)

        ct = getToolByName(context, 'portal_catalog')
        purl = getToolByName(context, 'portal_url')
        ntp = getToolByName(context, 'portal_properties').navtree_properties
        stp = getToolByName(context, 'portal_properties').site_properties

        # Build result dict
        result = []
        # first the actions
        if actions is not None:
            for action_info in actions.get('portal_tabs', []):
                data = action_info.copy()
                data['title'] = _(data['title'], default=data['title'])
                result.append(data)

        # check whether we only want actions
        if stp.getProperty('disable_folder_sections', None):
            return result

        custom_query = getattr(context, 'getCustomNavQuery', None)
        if custom_query is not None and utils.safe_callable(custom_query):
            query = custom_query()
        else:
            query = {}

        portal_path = purl.getPortalPath()
        query['path'] = {'query':portal_path, 'navtree':1}

        query['portal_type'] = utils.typesToList(context)

        if ntp.getProperty('sortAttribute', False):
            query['sort_on'] = ntp.sortAttribute

        if (ntp.getProperty('sortAttribute', False) and
            ntp.getProperty('sortOrder', False)):
            query['sort_order'] = ntp.sortOrder

        if ntp.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = ntp.wf_states_to_show

        query['is_default_page'] = False
        query['is_folderish'] = True

        # Get ids not to list and make a dict to make the search fast
        ids_not_to_list = ntp.getProperty('idsNotToList', ())
        excluded_ids = {}
        for exc_id in ids_not_to_list:
            excluded_ids[exc_id]=1

        rawresult = ct(**query)

        # now add the content to results
        for item in rawresult:
            if not (excluded_ids.has_key(item.getId) or item.exclude_from_nav):
                id, item_url = get_view_url(item)
                data = {'title': utils.pretty_title_or_id(context, item),
                        'id':id, 'url': item_url,
                        'description':item.Description}
                result.append(data)
        return result

class CatalogNavigationBreadcrumbs(utils.BrowserView):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        context = utils.context(self)
        request = self.request
        ct = getToolByName(context, 'portal_catalog')
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

        # Build result dict
        result = []
        for r_tuple in dec_result:
            item = r_tuple[1]
            id, item_url = get_view_url(item)
            data = {'Title': utils.pretty_title_or_id(context, item),
                    'absolute_url': item_url}
            result.append(data)
        return result

class CatalogNavigationStructure(CatalogNavigationTabs,
                                 CatalogNavigationBreadcrumbs,
                                 CatalogNavigationTree):
    implements(INavigationStructure)


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
            return (
                {'absolute_url': item_url,
                 'Title': utils.pretty_title_or_id(context, context),
                 }
                )

        view = getView(container, 'nav_view', request)
        base = tuple(view.breadcrumbs())

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        # don't show default pages in breadcrumbs
        if not utils.isDefaultPage(context, request):
            base += (
                     {'absolute_url': item_url,
                      'Title': utils.pretty_title_or_id(context, context),
                     },
                    )

        return base

class PhysicalNavigationStructure(PhysicalNavigationBreadcrumbs,
                                  CatalogNavigationTabs,
                                  CatalogNavigationTree):
    implements(INavigationStructure)

class RootPhysicalNavigationStructure(utils.BrowserView,
                                      CatalogNavigationTabs,
                                      CatalogNavigationTree):
    implements(INavigationStructure)

    def breadcrumbs(self):
        # XXX Root never gets included, it's hardcoded as 'Home' in
        # the template. We will fix and remove the hardcoding and fix
        # the tests.
        context = utils.context(self)
        return ()
