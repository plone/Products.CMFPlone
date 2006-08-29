from zope.interface import Interface
from zope.app.container.interfaces import IAdding

class IPortletAdding(IAdding):
    """Marker interface for the add view for portlet managers.
    
    Portlet add views should be registered for this interface.
    """

class IManagePortletsView(Interface):
    """The screen used to manage portlets in a particular context.
    """