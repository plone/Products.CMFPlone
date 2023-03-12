from plone.base.interfaces import ISearchSchema
from plone.base.interfaces.siteroot import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import implementer

import warnings


@implementer(ISearchSchema)
class SearchControlPanelAdapter:
    adapts(IPloneSiteRoot)

    def __init__(self, context):
        warnings.warn(
            f"Usage of bbb controlpanel '{self.__class__.__name__}' is deprecated."
            "Use registry record plone.base.interfaces.ISearchSchema instead."
            "It will be removed in Plone 6.1",
            DeprecationWarning,
        )
        self.portal = getSite()
        registry = getUtility(IRegistry)
        self.search_settings = registry.forInterface(ISearchSchema, prefix="plone")

    def get_enable_livesearch(self):
        return self.search_settings.enable_livesearch

    def set_enable_livesearch(self, value):
        if value:
            self.search_settings.enable_livesearch = True
        else:
            self.search_settings.enable_livesearch = False

    enable_livesearch = property(get_enable_livesearch, set_enable_livesearch)

    def get_types_not_searched(self):
        return self.search_settings.types_not_searched

    def set_types_not_searched(self, value):
        self.search_settings.types_not_searched = value

    types_not_searched = property(get_types_not_searched, set_types_not_searched)

    @property
    def sort_on(self):
        return self.search_settings.sort_on

    @sort_on.setter
    def sort_on(self, value):
        self.search_settings.sort_on = value
