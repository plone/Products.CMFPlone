from zope.interface import implements
from zope.component import getViewProviding

from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IDefaultPage
from Products.CMFPlone.browser.interfaces import INavigationRoot
from Products.CMFPlone.browser.interfaces import INavigationStructure
from Products.CMFPlone.interfaces.BrowserDefault import IBrowserDefault

class DefaultPage(utils.BrowserView):
    implements(IDefaultPage)

    def isDefaultPage(self, obj, context_):
        """Finds out if the given obj is the default page in its parent folder.

        Only considers explicitly contained objects, either set as index_html,
        with the default_page property, or using IBrowserDefault.
        """
        parentDefaultPage = self.getDefaultPage(context_)
        if parentDefaultPage is None or '/' in parentDefaultPage:
            return False
        return (parentDefaultPage == obj.getId())

    def getDefaultPage(self, context_):
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


class CatalogNavigationStructure(utils.BrowserView):
    implements(INavigationStructure)

    def breadcrumbs(self):
        context = utils.context(self)
        request = self.request
        ct = getToolByName(context, 'portal_catalog')
        stp = getToolByName(context, 'portal_properties').site_properties
        view_action_types = stp.getProperty('typesUseViewActionInListings')
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
            item_url = (item.portal_type in view_action_types and
                         item.getURL() + '/view') or item.getURL()
            data = {'Title': utils.pretty_title_or_id(context, item),
                    'absolute_url': item_url}
            result.append(data)
        return result

def get_view_url(context):
    stp = getToolByName(context, 'portal_properties').site_properties
    view_action_types = stp.getProperty('typesUseViewActionInListings')

    item_url = context.absolute_url()
    name = context.getId()

    if context.getPortalTypeName() in view_action_types:
        item_url += '/view'
        name += '/view'

    return name, item_url

class PhysicalNavigationStructure(utils.BrowserView):
    implements(INavigationStructure)

    def breadcrumbs(self):
        context = utils.context(self)
        container = utils.parent(context)
        request = self.request

        name, item_url = get_view_url(context)

        if container is None:
            return (
                {'absolute_url': item_url,
                 'Title': utils.pretty_title_or_id(context, context),
                 }
                )

        view = getViewProviding(container, INavigationStructure, request)
        base = tuple(view.breadcrumbs())

        if base:
            item_url = '%s/%s' % (base[-1]['absolute_url'], name)

        base += (
            {'absolute_url': item_url,
             'Title': utils.pretty_title_or_id(context, context),
             },
            )

        return base

class RootPhysicalNavigationStructure(utils.BrowserView):
    implements(INavigationStructure)

    def breadcrumbs(self):
        # XXX Root never gets included, it's hardcoded as 'Home' in
        # the template. We will fix and remove the hardcoding and fix
        # the tests.
        context = utils.context(self)
        return ()
