from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter

from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.http import IHTTPRequest

from Products.Five.browser import BrowserView

from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IPortletManagerView

class PortletManagerView(BrowserView):
    implements(IPortletManagerView)
    adapts(Interface, IHTTPRequest)
    
    __name__ = 'portletmanager' # Keep Zope 2 happy
    
    context = None # Will be set by BrowserView's __init__()
    manager = None # Will be set by publishTraverse() below
    
class PortletManagerTraverser(BrowserView):
    implements(IPublishTraverse)
    adapts(IPortletManagerView, IHTTPRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        """Use the traversing name to locate refer to a portlet manager.
        """
        self.context.manager = name
        
        # Find the name of the view to render and return it. In doing so,
        # we must also fix up the URL, since Zope won't add it for us
        # once we've popped it off the traversal name stack.
        
        viewName = request['TraversalRequestNameStack'].pop()
        request['URL'] += '/' + viewName
        request['ACTUAL_URL'] += '/' + viewName
        
        if viewName.startswith('@@'):
            viewName = viewName[2:]
        view = getMultiAdapter((self.context, self.request), name=viewName)
        return view.__of__(self.context.context)
