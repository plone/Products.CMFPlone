from zope.interface import Interface

from zope import schema
from zope.configuration import fields as configuration_fields

from zope.app.i18n import ZopeMessageFactory as _

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
        default=u"cmf.ManagePortal"
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