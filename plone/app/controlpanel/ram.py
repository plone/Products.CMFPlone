from plone.app.form.validators import null_validator

from zope.interface import Interface
from zope.component import adapts
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.ramcache.interfaces.ram import IRAMCache
from zope.schema import Int

from Acquisition import aq_inner

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.controlpanel.form import ControlPanelForm

from plone.protect import CheckAuthenticator


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

    base_template = ControlPanelForm.template
    template = ZopeTwoPageTemplateFile('ram.pt')

    form_fields = form.FormFields(IRAMCacheSchema)

    label = _("RAM Cache Settings")
    description = None
    form_name = _("RAM Cache Settings")

    def getStatistics(self):
        return getUtility(IRAMCache).getStatistics()

    def restricted_actions(self):
        return [a for a in self.actions.actions
                  if a.__name__ in ('form.actions.save', 'form.actions.cancel')]

    @form.action(_(u'Clear cache'), validator=null_validator, name=u'clearall')
    def handle_clearall_action(self, action, data):
        CheckAuthenticator(self.request)
        getUtility(IRAMCache).invalidateAll()
        self.status = _(u'Cleared the cache.')

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
            self._on_save(data)
        else:
            self.status = _("No changes made.")

    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        url = getMultiAdapter((self.context, self.request),
                              name='absolute_url')()
        self.request.response.redirect(url + '/plone_control_panel')
        return ''
