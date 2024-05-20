from plone.base.interfaces import IFilterSchema
from plone.base.interfaces import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


@adapter(IPloneSiteRoot)
@implementer(IFilterSchema)
class FilterControlPanelAdapter:
    def __init__(self, context):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IFilterSchema, prefix="plone")

    def get_disable_filtering(self):
        return self.settings.disable_filtering

    def set_disable_filtering(self, value):
        self.settings.disable_filtering = value

    def get_nasty_tags(self):
        return self.settings.nasty_tags

    def set_nasty_tags(self, value):
        self.settings.nasty_tags = value

    def get_valid_tags(self):
        return self.settings.valid_tags

    def set_valid_tags(self, value):
        self.settings.valid_tags = value

    def get_custom_attributes(self):
        return self.settings.custom_attributes

    def set_custom_attributes(self, value):
        self.settings.custom_attributes = value

    custom_attributes = property(get_custom_attributes, set_custom_attributes)
    valid_tags = property(get_valid_tags, set_valid_tags)
    nasty_tags = property(get_nasty_tags, set_nasty_tags)
    disable_filtering = property(get_disable_filtering, set_disable_filtering)
