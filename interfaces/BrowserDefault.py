try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

from Interface import Attribute

class IBrowerDefault(Interface):
    """
    Interface for content supporting selectable default views, either as a
    page template, or as the id of a contained object (inside a folderish item
    only). 
    """
    
    default_view = Attribute('The id of the page template that is the default view of the object')
    suppl_views = Attribute('A tuple of page template ids for additional selectable views')

    # Note that Plone's browserDefault is very scary. This method should delegate
    # to PloneTool.browserDefault() if at all possible. browserDefault() is
    # aware of IBrowserDefault and will do the right thing wrt. layouts and
    # default pages. 
    
    def __browser_default__():
        """
        Resolve what should be displayed when viewing this object without an
        explicit template specified. If a default page is set 
        (see setDefaultPage), resolve and return that. If not, resolve and
        return the page template found by getDefaultLayout().
        """

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

    def getDefaultPage():
        """
        Return the id of the default page, or None if none is set.
        """

    def hasDefaultPage():
        """
        Return True if this object has a default page set.
        """

    def getLayout():
        """
        Get the selected layout template.
        """

    def setLayout(layout):
        """
        Set the layout as the current view. 'layout' should be one of the list
        returned by getAvailableLayouts(). If a default page has been set
        with setDefaultPage(), it is turned off by calling setDefaultPage(None).
        """

    def getDefaultLayout():
        """
        Get the default layout template.
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

    def getTemplateFor(layout, default='base_view'):
        """
        Resolve the given layout to a page template object. If the layout
        cannot be found, fall back on the default_view set as a class attribute.
        If this is not found, fall back on the id supplied as 'default'.
        """
