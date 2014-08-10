import zope.interface
import zope.component
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from plone.registry.interfaces import IPersistentField
from plone.registry.field import PersistentField
from plone.registry.field import DisallowedProperty, StubbornProperty, InterfaceConstrainedProperty

from Products.CMFPlone import PloneMessageFactory as _

class IPatternRegistry(zope.interface.Interface):

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
        description=_(u"Coma separated values of pattern for shim"),
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

    skin_name = schema.List(
        title=_(u"Skins where is it rendered"),
        description=_(u"Empty means all skin name"),
        value_type=schema.Choice(
            title=_(u"Choose one skin name"),
            vocabulary='plone.app.vocabularies.Skins'
        ),
        required=False)

    enabled = schema.Bool(
        title=_(u"It's enabled?"),
        default=True,
        required=False)

class IPatternRegistryField(zope.interface.Interface):
    pass

@zope.interface.implementer(IPatternRegistryField)
class PatternRegistryField(schema.Object):
    pass

@zope.interface.implementer(IPatternRegistry)
class PatternRegistry(PersistentField, PatternRegistryField):

    url = FieldProperty(IPatternRegistry['url'])
    js = FieldProperty(IPatternRegistry['js'])
    css = FieldProperty(IPatternRegistry['css'])
    init = FieldProperty(IPatternRegistry['init'])
    deps = FieldProperty(IPatternRegistry['deps'])
    export = FieldProperty(IPatternRegistry['export'])
    conf = FieldProperty(IPatternRegistry['conf'])
    bundle = FieldProperty(IPatternRegistry['bundle'])
    condition = FieldProperty(IPatternRegistry['condition'])
    enabled = FieldProperty(IPatternRegistry['enabled'])
    name = FieldProperty(IPatternRegistry['name'])


class IPatternsRegistrySettings(zope.interface.Interface):
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


    registry = schema.List(title=_(u"Patterns registry"),
        value_type=PatternRegistryField(title=_(u"Pattern"), schema=IPatternRegistry)
    )


@zope.interface.implementer(IPersistentField)
@zope.component.adapter(IPatternRegistryField)
def persistentFieldAdapter(context):
    class_name = context.__class__.__name__
    persistent_class = PatternRegistry
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

