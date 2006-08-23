from zope.interface import Interface, Attribute

from zope.publisher.interfaces.browser import IBrowserView
from zope.app.container.interfaces import IAdding

from OFS.interfaces import IFolder

class IPortletManagerFolder(IFolder):
    """Marker interface for folders that contain portlet manager instances.
    """
    
class IPortletManagerView(IBrowserView):
    """The @@portletmanager view.
    
    We use this to provide a custom IPublishTraverse adapter that can look
    up portlet managers.
    """
    
    context = Attribute("The current content context")
    manager = Attribute("The id of the portlet manager")
    
class IPortletAdding(IAdding):
    """Marker interface for the add view for portlet managers.
    
    Portlet add views should be registered for this interface.
    """
    