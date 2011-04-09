from zope.interface import Interface

from zope import schema
from zope.configuration import fields as configuration_fields

from zope.publisher.interfaces.browser import IDefaultBrowserLayer, IBrowserView
from plone.portlets.interfaces import IPortletManager

from plone.app.portlets import PloneMessageFactory as _


class IPortletDirective(Interface):
    """Directive which registers a new portlet type.

    The portlet should also be installed into a site using a GenericSetup
    portlets.xml file, for example.
    """

    name = schema.TextLine(
        title=_(u"Name"),
        description=_(u"A unique name for the portlet. Also used for its add view."),
        required=True)

    interface = configuration_fields.GlobalInterface(
        title=_(u"Assignment type interface"),
        description=_(u"Should correspond to the public interface of the assignment"),
        required=True)

    assignment = configuration_fields.GlobalObject(
        title=_(u"Assignment class"),
        description=_(u"A persistent class storing the portlet assignment"),
        required=True)

    view_permission = schema.TextLine(
        title=_(u"View permission"),
        description=_(u"Permission used for viewing the portlet."),
        required=False,
        default=u"zope2.View"
        )

    edit_permission = schema.TextLine(
        title=_(u"Edit permission"),
        description=_(u"Permission used for editing the portlet assignment."),
        required=False,
        default=u"plone.app.portlets.ManageOwnPortlets"
        )

    renderer = configuration_fields.GlobalObject(
        title=_(u"Renderer"),
        description=_(u"A class which renders the portlet data provider"),
        required=True
        )

    addview = configuration_fields.GlobalObject(
        title=_(u"Add view"),
        description=_(u"View used to add the assignment object"),
        required=True
        )

    editview = configuration_fields.GlobalObject(
        title=_(u"Edit view"),
        description=_(u"View used to edit the assignment object (if appropriate)"),
        required=False
        )


class IPortletRendererDirective(Interface):
    """Register a portlet renderer, i.e. a different view of a portlet
    """

    # The portlet data provider type must be given

    portlet = configuration_fields.GlobalObject(
        title=_("Portlet data provider type for which this renderer is used"),
        description=_("An interface or class"),
        required=True)

    # Use either class or template to specify the custom renderer

    class_ = configuration_fields.GlobalObject(
        title=_("Class"),
        description=_("A class acting as the renderer."),
        required=False,
        )

    template = configuration_fields.Path(
        title=_(u"The name of a template that implements the renderer."),
        description=_(u"If given, the default renderer for this portlet will be used, but with this template"),
        required=False
        )

    # Use these to discriminate the renderer.

    for_ = configuration_fields.GlobalObject(
        title=_("Context object type for which this renderer is used"),
        description=_("""An interface or class"""),
        required=False,
        default=Interface,
        )

    layer = configuration_fields.GlobalObject(
        title=_("Browser layer for which this renderer is used"),
        description=_("""An interface or class"""),
        required=False,
        default=IDefaultBrowserLayer,
        )

    view = configuration_fields.GlobalObject(
        title=_("Browser view type for this this renderer is used"),
        description=_("An interface or class"),
        required=False,
        default=IBrowserView)

    manager = configuration_fields.GlobalObject(
        title=_("Portlet manager type for which this renderer is used"),
        description=_("An interface or class"),
        required=False,
        default=IPortletManager)
