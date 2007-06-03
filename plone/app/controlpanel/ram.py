from zope.app.cache.interfaces.ram import IRAMCache
from plone.app.controlpanel import form

from zope.interface import Interface
from zope.component import adapts
from zope.component import getUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Int

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from plone.app.controlpanel.form import ControlPanelForm


class IRAMCacheSchema(Interface):

    maxEntries = Int(title=_(u'A maximum number of cached values.'),
                     default=1000,
                     required=True)

    maxAge = Int(title=_(u'Maximum age for cached values in seconds.'),
                 default=3600,
                 required=True)

    cleanupInterval = Int(title=_(u"An interval between cache cleanups "
                                   "in seconds."),
                 default=300,
                 required=True)


class RAMCacheControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IRAMCacheSchema)

    def get_max_entries(self):
        return getUtility(IRAMCache).maxEntries
    
    def set_max_entries(self, value):
        getUtility(IRAMCache).maxEntries = value
    
    maxEntries = property(get_max_entries, set_max_entries)
    
    def get_max_age(self):
        return getUtility(IRAMCache).maxAge
    
    def set_max_age(self, value):
        getUtility(IRAMCache).maxAge = value
    
    maxAge = property(get_max_age, set_max_age)
    
    def get_cleanup_intervall(self):
        return getUtility(IRAMCache).cleanupInterval
    
    def set_cleanup_intervall(self, value):
        getUtility(IRAMCache).cleanupInterval = value
    
    cleanupInterval = property(get_cleanup_intervall, set_cleanup_intervall)


class RAMCacheControlPanel(ControlPanelForm):

    base_template = form._template
    template = ZopeTwoPageTemplateFile('ram.pt')

    form_fields = FormFields(IRAMCacheSchema)

    label = _("RAM Cache Settings")
    description = None
    form_name = _("RAM Cache Settings")

    def getStatistics(self):
        return getUtility(IRAMCache).getStatistics()
