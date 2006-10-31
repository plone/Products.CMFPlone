from Acquisition import Explicit
from OFS.SimpleItem import SimpleItem

from zope.interface import Interface, implements
from zope.component import adapts

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView

from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager

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
        
    @property
    def title(self):
        return self.template

    @property
    def available(self):
        """Property specifying that this portlet is always available
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
    
        from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
        ...
        render = ZopeTwoPageTemplateFile('mytemplate.pt')
        
    This will render the template mytemplate.pt, found in the same directory
    as your source code file.
    """
    
    implements(IPortletRenderer)


    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        self.data = data

    def update(self):
        pass

    def render(self):
        raise NotImplemented, "You must implement 'render' as a method or page template file attribute"