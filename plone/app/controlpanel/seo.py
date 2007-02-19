from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr
from form import ControlPanelForm
from persistent import Persistent
from wicked.plone.registration import basic_type_regs
from wicked.txtfilter import BrackettedWickedFilter
from zope.annotation.interfaces import IAnnotations
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import Interface, implements
from zope.schema import Int, TextLine, SourceText
from zope.schema import Tuple, Bool, Choice
from zope.schema.vocabulary import SimpleVocabulary


def propify(func):
    return property(**func())

class ISeoSchema(Interface):

    enable_sitemap = Bool(title=_(u'Provide sitemap.xml.gz in the portal root'),
                            description=_(u"""A sitemap.xml.gz file might be useful for Google and lists all your content along with modification dates"""),
                            default=False)


class SeoControlPanelAdapter(SchemaAdapterBase):    

    adapts(IPloneSiteRoot)
    implements(ISeoSchema)
    
    def __init__(self, context):
        super(SeoControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.site_properties
        self.jstool=getToolByName(context, 'portal_javascripts')

    def get_enable_sitemap(self):
        return getattr(self.context, 'webstats_js', True)

    def set_enable_sitemap(self, value):
        if value:
            self.context.manage_changeProperties(enable_sitemap=True)
        else:
            self.context.manage_changeProperties(enable_sitemap=False)

    enable_sitemap = property(get_enable_sitemap, set_enable_sitemap)

class SeoControlPanel(ControlPanelForm):
    form_fields = FormFields(ISeoSchema)
    label = _("SEO and Analytics Settings")
    description = _("Select which SEO-Functions you want to enable and provide data for web analytic packages")
    form_name = label
