from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from form import ControlPanelForm

class ISiteSchema(Interface):

    enable_sitemap = Bool(title=_(u'Provide sitemap.xml.gz in the portal root'),
                          description=_(u"""A sitemap.xml.gz file might be
                                        useful for Google and lists all your
                                        content along with modification dates"""),
                          default=False)


class SiteControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISiteSchema)

    def __init__(self, context):
        super(SiteControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.site_properties

    def get_enable_sitemap(self):
        return getattr(self.context, 'enable_sitemap', True)

    def set_enable_sitemap(self, value):
        self.context.manage_changeProperties(enable_sitemap=value)

    enable_sitemap = property(get_enable_sitemap, set_enable_sitemap)


class SiteControlPanel(ControlPanelForm):

    form_fields = FormFields(ISiteSchema)

    label = _("Site settings")
    description = _("Site-wide settings.")
    form_name = _("Site details")
