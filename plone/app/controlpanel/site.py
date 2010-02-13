from plone.locking.interfaces import ILockSettings
from zope.app.form.browser import TextAreaWidget
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import SourceText
from zope.site.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode

from form import ControlPanelForm


class ISiteSchema(ILockSettings):

    site_title = TextLine(title=_(u'Site title'),
                          description=_(u"This shows up in the title bar of "
                                        "browsers and in syndication feeds."),
                          default=u'')

    site_description = Text(title=_(u'Site description'),
                           description=_(u"The site description is available "
                               "in syndicated content and in search engines. "
                               "Keep it brief."),
                           default=u'',
                           required=False)

    exposeDCMetaTags = Bool(title=_(u"Expose Dublin Core metadata"),
                        description=_(u"Exposes the Dublin Core properties as metatags."),
                        default=False,
                        required=False)

    enable_sitemap = Bool(title=_(u"Expose sitemap.xml.gz"),
                          description=_(u"Exposes your content as a file "
                              "according to the sitemaps.org standard. You "
                              "can submit this to compliant search engines "
                              "like Google, Yahoo and Microsoft. It allows "
                              "these search engines to more intelligently "
                              "crawl your site."),
                          default=False,
                          required=False)

    webstats_js = SourceText(title=_(u'JavaScript for web statistics support'),
                        description=_(u"For enabling web statistics support "
                              "from external providers (for e.g. Google "
                              "Analytics). Paste the code snippets provided. "
                              "It will be included in the rendered HTML as "
                              "entered near the end of the page."),
                        default=u'',
                        required=False)


class SiteControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISiteSchema)

    def __init__(self, context):
        super(SiteControlPanelAdapter, self).__init__(context)
        self.portal = getSite()
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = pprop.site_properties
        self.encoding = pprop.site_properties.default_charset

    def get_site_title(self):
        title = getattr(self.portal, 'title', u'')
        return safe_unicode(title)

    def set_site_title(self, value):
        self.portal.title = value.encode(self.encoding)

    def get_site_description(self):
        description = getattr(self.portal, 'description', u'')
        return safe_unicode(description)

    def set_site_description(self, value):
        if value is not None:
            self.portal.description = value.encode(self.encoding)
        else:
            self.portal.description = ''

    def get_webstats_js(self):
        description = getattr(self.context, 'webstats_js', u'')
        return safe_unicode(description)

    def set_webstats_js(self, value):
        if value is not None:
            self.context.webstats_js = value.encode(self.encoding)
        else:
            self.context.webstats_js = ''

    site_title = property(get_site_title, set_site_title)
    site_description = property(get_site_description, set_site_description)
    webstats_js = property(get_webstats_js, set_webstats_js)

    enable_sitemap = ProxyFieldProperty(ISiteSchema['enable_sitemap'])
    exposeDCMetaTags = ProxyFieldProperty(ISiteSchema['exposeDCMetaTags'])


class MiniTextAreaWidget(TextAreaWidget):

    height = 3


class SmallTextAreaWidget(TextAreaWidget):

    height = 5


class SiteControlPanel(ControlPanelForm):

    form_fields = form.FormFields(ISiteSchema)
    form_fields['site_description'].custom_widget = MiniTextAreaWidget
    form_fields['webstats_js'].custom_widget = SmallTextAreaWidget

    label = _("Site settings")
    description = _("Site-wide settings.")
    form_name = _("Site settings")
