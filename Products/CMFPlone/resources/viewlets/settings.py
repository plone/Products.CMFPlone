from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

_ = MessageFactory('plone')


class IResourceRegistriesSettings(Interface):
    """Settings stored in portal_registry
    """

    resourceBundlesForThemes = schema.Dict(
        title=_(u"Resource bundles for themes"),
        description=_(u"Maps skin names to lists of resource bundle names"),
        key_type=schema.ASCIILine(),
        value_type=schema.List(value_type=schema.ASCIILine())
    )
