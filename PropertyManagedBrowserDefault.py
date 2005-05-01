from Products.CMFPlone.interfaces.BrowserDefault import ISelectableBrowserDefault

from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

class PropertyManagedBrowserDefault:
    """Mixin class which can provide ISelectableBrowserDefault behavior
    on objects, managing the vocabulary of selectable view templates as
    a property called 'selectable_views' on the object (assumed to exist)
    and storing the actual selection as an internal variable.
    """
    
    __implements__ = (ISelectableBrowserDefault, )

    security = ClassSecurityInfo()

    security.declareProtected(CMFCorePermissions.View, 'defaultView')
    def defaultView(self, request=None):
        """
        Get the actual view to use. If a default page is set, its id will
        be returned. Else, the current layout's page template id is returned.
        """
        if self.isPrincipiaFolderish and self.getDefaultPage():
            return self.getDefaultPage()
        else:
            return self.getLayout()

    def __browser_default__(self, request):
        """
        Resolve what should be displayed when viewing this object without an
        explicit template specified. If a default page is set, resolve and
        return that. If not, resolve and return the page template found by
        getLayout().
        """
        return getToolByName(self, 'plone_utils').browserDefault(self)
        

    security.declareProtected(CMFCorePermissions.View, 'getDefaultPage')
    def getDefaultPage(self):
        """
        Return the id of the default page, or None if none is set. The default
        page must be contained within this (folderish) item.
        """
        return getattr(aq_base(self), '_selected_default_page', None)
        

    security.declareProtected(CMFCorePermissions.View, 'getLayout')
    def getLayout(self, **kw):
        """
        Get the selected layout template. Note that a selected default page
        will override the layout template.
        """
        return getattr(aq_base(self), '_selected_layout', self.getDefaultLayout())

    def getDefaultLayout(self):
        """
        Get the default layout template. This is the first one in the list,
        falling back on 'view' if the list is empty.
        """
        layouts = self.getAvailableLayouts()
        if layouts:
            return layouts[0][0]
        else:
            return 'view'
        

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        """
        Return True if the user has permission to select a default page on this
        (folderish) item, and the item is folderish.
        """
        if not self.isPrincipiaFolderish:
            return False
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        return member.has_permission(CMFCorePermissions.ModifyPortalContent, self)

    security.declarePublic('canSetLayout')
    def canSetLayout(self):
        """
        Return True if the current authenticated user is permitted to select
        a layout.
        """
        mtool = getToolByName(self, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        return member.has_permission(CMFCorePermissions.ModifyPortalContent, self)
        
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setDefaultPage')
    def setDefaultPage(self, objectId):
        """
        Set the default page to display in this (folderish) object. The objectId
        must be a value found in self.objectIds() (i.e. a contained object).
        This object will be displayed as the default_page/index_html object
        of this (folderish) object. This will override the current layout
        template returned by getLayout(). Pass None for objectId to turn off
        the default page and return to using the selected layout template.
        """
        self._selected_default_page = objectId
        self._p_changed = 1

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setLayout')
    def setLayout(self, layout):
        """
        Set the layout as the current view. 'layout' should be one of the list
        returned by getAvailableLayouts(). If a default page has been set
        with setDefaultPage(), it is turned off by calling setDefaultPage(None).
        """
        self._selected_layout = layout
        self._p_changed = 1
        self.setDefaultPage(None)

    security.declareProtected(CMFCorePermissions.View, 'getAvailableLayouts')
    def getAvailableLayouts(self):
        """
        Get the layouts registered for this object.
        """
        views = self.getProperty('selectable_views', [])
        tuples = []
        
        # We need to look up the title, but doing so requires traversing to
        # each item in the list of views. Hence we cache it. The cache is
        # fully invalidated if any views are not found. The title of a
        # page template should practically never change, but during development
        # it might, for instance. Similarly, the list of selectable views
        # should be very stable.
        
        cache = getattr(aq_base(self), '_selectable_views_cache', None)
        dirty = False
        
        if not cache:
            dirty = True
        else:
            examined = 0
            for view in views:
                title = cache.get(view, '__marker__')
                if title == '__marker__':
                    # title == '__marker__' means that cache doesn't have this view - invalidate
                    continue
                elif title is None:
                    # title == None means that template couldn't be found - ignore
                    examined += 1
                    continue
                else:
                    examined += 1
                    tuples.append((view, title,))
                    
            # Invalidate if any views were added or removed
            if examined != len(cache) or examined != len(views):
                dirty = True

        if dirty:
            cache = self.invalidateSelectableViewsCache()
            tuples = []
            for view in views:
                title = cache.get(view, None)
                if title:
                    tuples.append((view, title,))
        return tuples
        
    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 
                                'invalidateSelectableViewsCache')
    def invalidateSelectableViewsCache(self):
        """
        The titles of page templates available as selectable views are cached
        to avoid having to look them up each time. In practice, they should
        rarely if ever change, but call this method to invalidate the cache.
        
        Returns the cache object.
        """
        views = self.getProperty('selectable_views', [])
        cache = {}
        for view in views:
            obj = self.unrestrictedTraverse(view, None)
            if not obj:
                cache[view] = None
            else:
                cache[view] = obj.title_or_id()
        self._selectable_views_cache = cache
        self._p_changed = 1
        return self._selectable_views_cache