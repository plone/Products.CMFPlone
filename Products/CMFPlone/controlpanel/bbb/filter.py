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

    nasty_tags = property(get_nasty_tags, set_nasty_tags)
    disable_filtering = property(get_disable_filtering, set_disable_filtering)
