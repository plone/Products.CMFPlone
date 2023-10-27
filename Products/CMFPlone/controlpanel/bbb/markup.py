from plone.base.interfaces import IMarkupSchema
from plone.base.interfaces.siteroot import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implementer

import warnings


@implementer(IMarkupSchema)
class MarkupControlPanelAdapter:
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        warnings.warn(
            f"Usage of bbb controlpanel '{self.__class__.__name__}' is deprecated."
            "Use registry record plone.base.interfaces.IMarkupSchema instead."
            "It will be removed in Plone 6.1",
            DeprecationWarning,
        )
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
