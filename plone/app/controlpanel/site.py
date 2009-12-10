from zope.app.component.hooks import getSite
from zope.app.form.browser import TextAreaWidget
from zope.interface import Interface
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import SourceText
from zope.schema import Choice

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode

from form import ControlPanelForm

from plone.locking.interfaces import ILockSettings

class ISiteSchema(Interface):

    site_title = TextLine(title=_(u'Site title'),
                          description=_(u"This shows up in the title bar of "
                                        "browsers, in syndication feeds, "
                                        "etc."),
                          default=u'')

    site_description = Text(title=_(u'Site description'),
                           description=_(u"The site description is available "
                               "in syndicated content and in search engines. "
                               "Keep it brief."),
                           default=u'',
                           required=False)

    visible_ids = Bool(title=_(u"Show 'Short Name' on content?"),
                       description=_(u"Display and allow users to edit the "
                           "'Short name' content identifiers, which form the "
                           "URL part of a content item's address. Once "
                           "enabled, users will then be able to enable this "
                           "option in their preferences."),
                       default=False,
                       required=False)

    enable_inline_editing = Bool(title=_(u"Enable inline editing"),
                                 description=_(u"Check this to enable "
                                                "inline editing on the site."),
                                 default=True,
                                 required=False)

    default_editor = Choice(title=_(u'Default editor'),
                            description=_(u"Select the default wysiwyg editor. "
                                "Users will be able to choose their own or "
                                "select to use the site default."),
                            default=u'TinyMCE',
                            missing_value=set(),
                            vocabulary="plone.app.vocabularies.AvailableEditors",
                            required=False)

    enable_link_integrity_checks = Bool(title=_(u"Enable link integrity "
                                                 "checks"),
                          description=_(u"Determines if the users should get "
                              "warnings when they delete or move content that "
                              "is linked from inside the site."),
                          default=True,
                          required=False)

    ext_editor = Bool(title=_(u'Enable External Editor feature'),
                          description=_(u"Determines if the external editor "
                              "feature is enabled. This feature requires a "
                              "special client-side application installed. The "
                              "users also have to enable this in their "
                              "preferences."),
                          default=False,
                          required=False)

    enable_sitemap = Bool(title=_(u"Expose sitemap.xml.gz in the portal root"),
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

    lock_on_ttw_edit = Bool(title=_(u"Enable locking for through-the-web edits"),
                          description=_(u"Disabling locking here will only "
                                "affect users editing content through the "
                                "Plone web UI.  Content edited via WebDAV "
                                "clients will still be subject to locking."),
                          default=True,
                          required=False)
                          
    exposeDCMetaTags = Bool(title=_(u"Expose Dublin Core metadata properties"),
                        description=_(u"Exposes the Dublin Core properties as metatags."),
                        default=False,
                        required=False)



class SiteControlPanelAdapter(SchemaAdapterBase):

    implements(ISiteSchema, ILockSettings)

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

    visible_ids = ProxyFieldProperty(ISiteSchema['visible_ids'])
    enable_inline_editing = ProxyFieldProperty(ISiteSchema['enable_inline_editing'])
    enable_link_integrity_checks = ProxyFieldProperty(ISiteSchema['enable_link_integrity_checks'])
    ext_editor = ProxyFieldProperty(ISiteSchema['ext_editor'])
    default_editor = ProxyFieldProperty(ISiteSchema['default_editor'])
    enable_sitemap = ProxyFieldProperty(ISiteSchema['enable_sitemap'])
    lock_on_ttw_edit = ProxyFieldProperty(ISiteSchema['lock_on_ttw_edit'])
    exposeDCMetaTags = ProxyFieldProperty(ISiteSchema['exposeDCMetaTags'])

class SmallTextAreaWidget(TextAreaWidget):

    height = 5


class SiteControlPanel(ControlPanelForm):

    form_fields = FormFields(ISiteSchema)
    form_fields['site_description'].custom_widget = SmallTextAreaWidget

    label = _("Site settings")
    description = _("Site-wide settings.")
    form_name = _("Site settings")
