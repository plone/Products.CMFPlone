from plone.base.interfaces import IMarkupSchema
from plone.base.interfaces.siteroot import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


@adapter(IPloneSiteRoot)
@implementer(IMarkupSchema)
class MarkupControlPanelAdapter:
    def __init__(self, context):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IMarkupSchema, prefix="plone")

    @property
    def default_type(self):
        return self.settings.default_type

    @default_type.setter
    def default_type(self, value):
        self.settings.default_type = value

    @property
    def allowed_types(self):
        return self.settings.allowed_types

    @allowed_types.setter
    def allowed_types(self, value):
        self.settings.allowed_types = value
