import sys

from Acquisition import Explicit
from OFS.SimpleItem import SimpleItem
from ZODB.POSException import ConflictError

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope.interface import Interface, implements
from zope.component import adapts

from zope.publisher.interfaces.browser import IBrowserView

from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager

from plone.app.portlets.interfaces import IDeferredPortletRenderer

from zope.app.container.contained import Contained

# Convenience imports
from plone.app.portlets.browser.formhelper import AddForm
from plone.app.portlets.browser.formhelper import NullAddForm
from plone.app.portlets.browser.formhelper import EditForm

class Assignment(SimpleItem, Contained):
    """Base class for assignments.
    
    Your type may override the 'title', 'available' and 'data' properties, and
    may 
    """
    
    implements(IPortletAssignment)
    
    __name__ = ''
    
    @property
    def id(self):
        return getattr(self, '__name__', '')
    
    @property
    def title(self):
        return self.template

    def available(self, context, request):
        """By default, this portlet is always available
        """
        return True

    @property
    def data(self):
        """Make the assignment itself represent the data object that is being rendered.
        """
        return self

class Renderer(Explicit):
    """Base class for portlet renderers.
    
    You must override render() to return a string to render. One way of 
    doing this is to write:
    
        from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
        ...
        render = ViewPageTemplateFile('mytemplate.pt')
        
    This will render the template mytemplate.pt, found in the same directory
    as your source code file.
    """
    
    implements(IPortletRenderer)

    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.view = view
        self.__parent__ = view
        self.manager = manager
        self.data = data

    def update(self):
        pass

    def render(self):
        raise NotImplementedError("You must implement 'render' as a method "
                                  "or page template file attribute")

    @property
    def available(self):
        """By default, portlets are available
        """
        return True
        
class DeferredRenderer(Renderer):
    """provide defer functionality via KSS
    
    in here don't override render() but instead override render_full
    
    """

    implements(IDeferredPortletRenderer)

    render_preload = ViewPageTemplateFile('deferred_portlet.pt')
    
    def render_full(self):
        raise NotImplemented, "You must implement 'render_full' as a method or page template file attribute"

    def render(self):
        """render the portlet

        the template gets choosen depending on the initialize state
        """
        if self.initializing:
            return self.render_preload()
        else:
            return self.render_full()

