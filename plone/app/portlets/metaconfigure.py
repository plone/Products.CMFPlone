from zope.interface import Interface, alsoProvides

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.interfaces import IPortletTypeInterface
from plone.app.portlets.browser.interfaces import IPortletAdding

from zope.component.zcml import adapter
from zope.component.zcml import utility

from zope.component.interfaces import IFactory
from zope.component.factory import Factory

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser.metaconfigure import page

# Keep track of which renderers we've registered so that we can artifically
# subclass them in portletRendererDirective. Yes, this is evil.
_default_renderers = {}


def portletDirective(_context, name, interface, assignment, renderer, addview,
        view_permission=u"zope2.View", edit_permission="plone.app.portlets.ManageOwnPortlets", editview=None):
    """Register a portlet assignment type using typical options.

    Portlets that consist of a simple assignment class deriving form
    base.Assignment, a renderer deriving from base.Renderer, an addview
    using formlib and deriving from base.AddForm and an editview (optional)
    using formlib and deriving from base.EditForm, can use this directive
    to avoid having to regiter each of those components individually.

    In addition, we register the portlet interface using IPortletTypeInterface
    and an IFactory utility, in order to help the GenericSetup handler and
    other generic code instantiate portlets.
    """

    # Register the portlet interface as named utility so that we can find it
    # again (in the GS handler)

    alsoProvides(interface, IPortletTypeInterface)
    utility(_context,
            provides=IPortletTypeInterface,
            name=name,
            component=interface)

    # Register a factory

    utility(_context,
            provides=IFactory,
            name=name,
            component=Factory(assignment))

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
    #        zope.publisher.interfaces.browser.IDefaultBrowserLayer
    #        zope.publisher.interfaces.browser.IBrowserView
    #        plone.portlets.interfaces.IPortletManager
    #        [interface]
    #   provides="plone.portlets.interfaces.IPortletRenderer"
    #   />

    adapter(_context, (renderer, ), provides=IPortletRenderer,
            for_=(Interface, IDefaultBrowserLayer, IBrowserView, IPortletManager, interface))
    _default_renderers[interface] = renderer

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
    #   name="edit"
    #   class="[editview]"
    #   permission="[edit_permission]"
    #   />

    if editview is not None:
        page(_context,
             for_=interface,
             name=u"edit",
             class_=editview,
             permission=edit_permission)


def portletRendererDirective(_context, portlet, class_=None, template=None,
        for_=Interface, layer=IDefaultBrowserLayer, view=IBrowserView, manager=IPortletManager):
    """Register a custom/override portlet renderer
    """

    if class_ is None and template is None:
        raise TypeError("Either 'template' or 'class' must be given")
    if class_ is not None and template is not None:
        raise TypeError("'template' and 'class' cannot be specified at the same time")

    if template is not None:

        # Look up the default renderer for this portlet
        base_class = _default_renderers.get(portlet, None)
        if base_class is None:
            raise TypeError("Can't find default renderer for %s. "
                            "Perhaps the portlet has not been registered yet?" % portlet.__identifier__)

        # Generate a subclass with 'renderer' using this template
        class_ = type("PortletRenderer from %s" % template.encode('UTF-8'),
                            (base_class, ), {'render': ViewPageTemplateFile(template)})

    adapter(_context, (class_, ), provides=IPortletRenderer,
                for_=(for_, layer, view, manager, portlet))
