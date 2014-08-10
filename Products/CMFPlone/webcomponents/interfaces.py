import zope.interface
import zope.component
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from plone.registry.interfaces import IPersistentField
from plone.registry.field import PersistentField
from plone.registry.field import DisallowedProperty, StubbornProperty, InterfaceConstrainedProperty

from Products.CMFPlone import PloneMessageFactory as _

class IWebComponent(zope.interface.Interface):

    name = schema.ASCIILine(
        title=_(u"Component name"),
        required=True)

    url = schema.ASCIILine(
        title=_(u"Resources base URL"),
        required=False)

    js = schema.ASCIILine(
        title=_(u"Main js file"),
        required=False)

    css = schema.List(
        title=_(u"CSS/LESS files"),
        value_type=schema.ASCIILine(title=_(u"URL")),
        default=[],
        required=False)

    init = schema.ASCIILine(
        title=_(u"Init instruction for shim"),
        required=False)

    deps = schema.ASCIILine(
        title=_(u"Dependencies for shim"),
        description=_(u"Coma separated values of webcomponents for shim"),
        required=False)

    export = schema.ASCIILine(
        title=_(u"Export vars for shim"),
        required=False)

    conf = schema.Text(
        title=_(u"Configuration in JSON for the widget"),
        description=_(u"Should be accessible on @@getWCconfig?id=name"),
        required=False)

    bundle = schema.Bool(
        title=_(u"Is it a bundle?"),
        description=_(u"In case it is a bundle it's going to be deployed on the js viewlet"),
        required=False)

    condition = schema.ASCIILine(
        title=_(u"Condition to render"),
        description=_(u"In case its a bundle we can have a condition to render it"),
        required=False)

    enabled = schema.Bool(
        title=_(u"It's enabled?"),
        required=False)

class IWebComponentField(zope.interface.Interface):
    pass

@zope.interface.implementer(IWebComponentField)
class WebComponentField(schema.Object):
    pass

@zope.interface.implementer(IWebComponent)
class WebComponent(PersistentField, WebComponentField):

    url = FieldProperty(IWebComponent['url'])
    js = FieldProperty(IWebComponent['js'])
    css = FieldProperty(IWebComponent['css'])
    init = FieldProperty(IWebComponent['init'])
    deps = FieldProperty(IWebComponent['deps'])
    export = FieldProperty(IWebComponent['export'])
    conf = FieldProperty(IWebComponent['conf'])
    bundle = FieldProperty(IWebComponent['bundle'])
    condition = FieldProperty(IWebComponent['condition'])
    enabled = FieldProperty(IWebComponent['enabled'])
    name = FieldProperty(IWebComponent['name'])


class IWebComponentsSettings(zope.interface.Interface):
    """
        Each web component may have :
            - url
            - js
            - bunch of css files
            - init (for shim)
            - deps (for shim)
            - export (for shim)
            - conf
            - name
            - if its a bundle
            - condition
            - if its enable
    """


    registry = schema.List(title=_(u"Web components registry"),
        value_type=WebComponentField(title=_(u"Web component"), schema=IWebComponent)
    )


@zope.interface.implementer(IPersistentField)
@zope.component.adapter(IWebComponentField)
def persistentFieldAdapter(context):
    class_name = context.__class__.__name__
    persistent_class = WebComponent
    if not issubclass(persistent_class, context.__class__):
        __traceback_info__ = "Can only clone a field of an equivalent type."
        return None
    
    ignored = list(DisallowedProperty.uses + StubbornProperty.uses)
    constrained = list(InterfaceConstrainedProperty.uses)
    
    instance = persistent_class.__new__(persistent_class)
    
    context_dict = dict([(k,v) for k,v in context.__dict__.items() 
                            if k not in ignored])

    for k,iface in constrained:
        v = context_dict.get(k, None)
        if v is not None and v != context.missing_value:
            v = iface(v, None)
            if v is None:
                __traceback_info__ = "The property `%s` cannot be adapted to `%s`." % (k, iface.__identifier__,)
                return None
            context_dict[k] = v

    instance.__dict__.update(context_dict)
    return instance

