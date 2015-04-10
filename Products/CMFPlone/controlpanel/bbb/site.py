# -*- coding: utf-8 -*-
from zope.schema.fieldproperty import FieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces import ISiteSchema
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements


class SiteControlPanelAdapter(object):

    adapts(IPloneSiteRoot)
    implements(ISiteSchema)

    def __init__(self, context):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISiteSchema, prefix="plone")

    def get_site_title(self):
        return self.settings.site_title

    def set_site_title(self, value):
        if isinstance(value, str):
            value = value.decode('utf-8')
        self.settings.site_title = value

    def get_webstats_js(self):
        return self.settings.webstats_js

    def set_webstats_js(self, value):
        if isinstance(value, str):
            value = value.decode('utf-8')
        self.settings.webstats_js = value

    site_title = property(get_site_title, set_site_title)
    webstats_js = property(get_webstats_js, set_webstats_js)

    site_logo = FieldProperty(ISiteSchema['site_logo'])
    enable_sitemap = FieldProperty(ISiteSchema['enable_sitemap'])
    exposeDCMetaTags = FieldProperty(ISiteSchema['exposeDCMetaTags'])
