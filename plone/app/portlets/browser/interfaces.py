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

class IManageContextualPortletsView(IManagePortletsView):
    """Marker for the manage contextual portlets view
    """

class IManageCurrentUserPortletsView(IManagePortletsView):
    """Marker for the manage contextual personal view
    """

class IManageUserPortletsView(IManagePortletsView):
    """Marker for the manage user portlets view
    """

class IManageGroupPortletsView(IManagePortletsView):
    """Marker for the manage group portlets view
    """

class IManageContentTypePortletsView(IManagePortletsView):
    """Marker for the manage content type portlets view
    """