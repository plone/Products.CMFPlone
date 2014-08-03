# -*- coding: utf-8 -*-
from zope.component import adapts
from Products.CMFPlone.interfaces import ILanguageSchema
from zope.interface import implements
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.registry.interfaces import IRegistry


class LanguageControlPanelAdapter(object):

    adapts(IPloneSiteRoot)
    implements(ILanguageSchema)

    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.navigation_settings = registry.forInterface(
            ILanguageSchema, prefix="plone")

    def get_default_language(self):
        return self.navigation_settings.default_language

    def set_default_language(self, value):
        self.navigation_settings.default_language = value

    default_language = property(get_default_language,
                                set_default_language)

    def get_use_combined_language_codes(self):
        return self.navigation_settings.use_combined_language_codes

    def set_use_combined_language_codes(self, value):
        self.navigation_settings.use_combined_language_codes = value

    use_combined_language_codes = property(get_use_combined_language_codes,
                                           set_use_combined_language_codes)
