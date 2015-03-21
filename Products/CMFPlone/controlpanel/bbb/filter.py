from Products.CMFPlone.interfaces import IFilterSchema
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements


class FilterControlPanelAdapter(object):

    adapts(IPloneSiteRoot)
    implements(IFilterSchema)

    def __init__(self, context):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IFilterSchema, prefix='plone')

    def get_disable_filtering(self):
        return self.settings.disable_filtering

    def set_disable_filtering(self, value):
        self.settings.disable_filtering = value

    def get_nasty_tags(self):
        return self.settings.nasty_tags

    def set_nasty_tags(self, value):
        self.settings.nasty_tags = value

    def get_stripped_tags(self):
        return self.settings.stripped_tags

    def set_stripped_tags(self, value):
        self.settings.stripped_tags = value

    def get_custom_tags(self):
        return self.settings.custom_tags

    def set_custom_tags(self, value):
        self.settings.custom_tags = value

    def get_stripped_attributes(self):
        return self.settings.stripped_attributes

    def set_stripped_attributes(self, value):
        self.settings.stripped_attributes = value

    def get_stripped_combinations(self):
        return self.settings.stripped_combinations

    def set_stripped_combinations(self, value):
        self.settings.stripped_combinations = value

    def get_style_whitelist(self):
        return self.settings.style_whitelist

    def set_style_whitelist(self, value):
        self.settings.style_whitelist = value

    def get_class_blacklist(self):
        return self.settings.class_blacklist

    def set_class_blacklist(self, value):
        self.settings.class_blacklist = value

    class_blacklist = property(get_class_blacklist, set_class_blacklist)
    style_whitelist = property(get_style_whitelist, set_style_whitelist)
    stripped_combinations = property(get_stripped_combinations,
                                     set_stripped_combinations)
    stripped_attributes = property(get_stripped_attributes,
                                   set_stripped_attributes)
    custom_tags = property(get_custom_tags, set_custom_tags)
    stripped_tags = property(get_stripped_tags, set_stripped_tags)
    nasty_tags = property(get_nasty_tags, set_nasty_tags)
    disable_filtering = property(get_disable_filtering, set_disable_filtering)
