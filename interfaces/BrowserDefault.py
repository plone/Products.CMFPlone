try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

from Interface import Attribute

class IBrowserDefault(Interface):
    """
    Interface for content supporting different views on a per-instance basis, 
    either as a page template, or as the id of a contained object (inside a 
    folderish item only). 
    """
        
    def defaultView(request=None):
        """
        Get the actual view to use. If a default page is set, its id will
        be returned. Else, the current layout's page template id is returned.
        """
    
    # Note that Plone's browserDefault is very scary. This method should delegate
    # to PloneTool.browserDefault() if at all possible. browserDefault() is
    # aware of IBrowserDefault and will do the right thing wrt. layouts and
    # default pages. 
    
    def __browser_default__(request):
        """
        Resolve what should be displayed when viewing this object without an
        explicit template specified. Returns a tuple (obj, [path, path]), where
        obj is the object to publish (usually self), and the list of paths is
        the list of page templates/object ids to try to use as the view for 
        this object.
        """

    def getDefaultPage():
        """
        Return the id of the default page, or None if none is set. The default
        page must be contained within this (folderish) item.
        """

    def getLayout():
        """
        Get the selected layout template. Note that a selected default page
        will override the layout template.
        """
        
    def getDefaultLayout():
        """
        Get the default layout template.
        """
    
class ISelectableBrowserDefault(IBrowserDefault):
    """
    Interface for content supporting operations to explicitly set the default
    layoute template or default page object.
    """
    
    
    default_view = Attribute('The id of the page template that is the default view of the object')
    suppl_views = Attribute('A tuple of page template ids for additional selectable views')

    def canSetDefaultPage():
        """
        Return True if the user has permission to select a default page on this
        (folderish) item, and the item is folderish.
        """

    def setDefaultPage(objectId):
        """
        Set the default page to display in this (folderish) object. The objectId
        must be a value found in self.objectIds() (i.e. a contained object).
        This object will be displayed as the default_page/index_html object
        of this (folderish) object. This will override the current layout
        template returned by getLayout(). Pass None for objectId to turn off
        the default page and return to using the selected layout template.
        """

    def setLayout(layout):
        """
        Set the layout as the current view. 'layout' should be one of the list
        returned by getAvailableLayouts(). If a default page has been set
        with setDefaultPage(), it is turned off by calling setDefaultPage(None).
        """
        
    def canSetLayout():
        """
        Return True if the current authenticated user is permitted to select
        a layout, and there is more than one layout to select.
        """
        
    def getAvailableLayouts():
        """
        Get the layouts registered for this object.
        """
