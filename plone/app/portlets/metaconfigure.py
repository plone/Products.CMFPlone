from zope.interface import Interface
from zope.component import provideAdapter

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.browser.interfaces import IPortletAdding

from Products.Five.browser.metaconfigure import page

def portletDirective(_context, name, interface, assignment, renderer, addview,
        view_permission=u"zope2.View", edit_permission="cmf.ManagePortal", editview=None):
    """Register a portlet assignment type using typical options. 
    
    Portlets that consist of a simple assignment class deriving form 
    base.Assignment, a renderer deriving from base.Renderer, an addview
    using formlib and deriving from base.AddForm and an editview (optional)
    using formlib and deriving from base.EditForm, can use this directive
    to avoid having to regiter each of those components individually.
    """

    # Set permissions on the assignment class
    
    # <class class="[assignment]">
    #   <require 
    #       permission="[view_permission]"
    #       interface="[interface]"
    #       />
    # </class>
    
    # XXX: Is this necessary? The renderer doesn't need it, so it may
    # just be superfluous.
    
    # Register the renderer:
    
    # <adapter 
    #   factory="[renderer]"
    #   for="zope.interface.Interface
    #        zope.publisher.interfaces.browser.IBrowserRequest
    #        zope.publisher.interfaces.browser.IBrowserView
    #        plone.portlets.interfaces.IPortletManager
    #        [interface]
    #   provides="plone.portlets.interfaces.IPortletRenderer"
    #   />
    
    provideAdapter(factory=renderer,
                   adapts=(Interface, IBrowserRequest, IBrowserView, IPortletManager, interface,),
                   provides=IPortletRenderer)
    
    # Register the adding view
    
    # <browser:page 
    #   for="plone.app.portlets.browser.interfaces.IPortletAdding"
    #   name="[name]"
    #   class="[addview]"
    #   permission="[edit_permission]"
    #   />
    
    page(_context, 
         for_=IPortletAdding,
         name=name,
         class_=addview,
         permission=edit_permission)
    
    # Register the edit view, if applicable
    
    # <browser:page 
    #   for="[interface]"
    #   name="edit.html"
    #   class="[editview]"
    #   permission="[edit_permission]"
    #   />
    
    if editview is not None:
        page(_context, 
             for_=interface,
             name=u"edit.html",
             class_=editview,
             permission=edit_permission)