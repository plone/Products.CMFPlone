from Products.CMFDynamicViewFTI.interfaces import ISelectableBrowserDefault

from Acquisition import aq_base, aq_inner
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

    def __call__(self):
        """
        Resolve the selected view template
        """
        template = self.unrestrictedTraverse(self.getLayout())
        context = aq_inner(self)
        template = template.__of__(context)
        return template(context, context.REQUEST)

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

    security.declareProtected(CMFCorePermissions.ModifyPortalContent, 'setLayout')
    def setLayout(self, layout):
        """
        Set the layout as the current view. 'layout' should be one of the list
        returned by getAvailableLayouts(). If a default page has been set
        with setDefaultPage(), it is turned off by calling setDefaultPage(None).
        """
        self._selected_layout = layout
        self.setDefaultPage(None)

    security.declareProtected(CMFCorePermissions.View, 'getAvailableLayouts')
    def getAvailableLayouts(self):
        """
        Get the layouts registered for this object.
        """
        views = self.getProperty('selectable_views', [])
        tuples = []
        for view in views:
            template = getattr(self, view, None)
            if template:
                tuples.append((template.getId(), template.title_or_id(),))
        return tuples

