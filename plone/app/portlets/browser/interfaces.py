from zope.interface import Interface
from zope.app.container.interfaces import IAdding

class IPortletAdding(IAdding):
    """Marker interface for the add view for portlet managers.
    
    Portlet add views should be registered for this interface.
    """

class IManagePortletsView(Interface):
    """The screen used to manage portlets in a particular context.
    """
    
    def getAssignmentMappingUrl(manager):
        """Given a portlet manager, get the URL to its assignment mapping.
        """
        
    def getAssignmentsForManager(manager):
        """Get the assignments in the current context for the given manager.
        """

class IManageDashboardPortletsView(IManagePortletsView):
    """Marker for the manage dashboard portlets view
    """

class IManageColumnPortletsView(IManagePortletsView):
    """Base class for views that should display the edit fuctionality
    for column portlets.
    
    This allows us to register a generic portlet manager renderer for this
    view that can apply to different categories of assignment.
    """

class IManageContextualPortletsView(IManageColumnPortletsView):
    """Marker for the manage contextual portlets view
    """
    
class IManageUserPortletsView(IManageColumnPortletsView):
    """Marker for the manage user portlets view
    """

class IManageGroupPortletsView(IManageColumnPortletsView):
    """Marker for the manage group portlets view
    """

class IManageContentTypePortletsView(IManageColumnPortletsView):
    """Marker for the manage content type portlets view
    """