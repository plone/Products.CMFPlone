from plone.base.interfaces import IPloneSiteRoot
from plone.base.interfaces import ISiteSchema
from plone.registry.interfaces import IRegistry
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty


@adapter(IPloneSiteRoot)
@implementer(ISiteSchema)
class SiteControlPanelAdapter:
    def __init__(self, context):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(ISiteSchema, prefix="plone")

    def get_site_title(self):
        return self.settings.site_title

    def set_site_title(self, value):
        self.settings.site_title = value

    def get_webstats_js(self):
        return self.settings.webstats_js

    def set_webstats_js(self, value):
        self.settings.webstats_js = value

    site_title = property(get_site_title, set_site_title)
    webstats_js = property(get_webstats_js, set_webstats_js)

    site_logo = FieldProperty(ISiteSchema["site_logo"])
    enable_sitemap = FieldProperty(ISiteSchema["enable_sitemap"])
    exposeDCMetaTags = FieldProperty(ISiteSchema["exposeDCMetaTags"])
