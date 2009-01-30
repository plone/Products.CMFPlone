from zope.interface import implements
from zope.component import getMultiAdapter
from zope.event import notify

from plone.fieldsets.form import FieldsetsEditForm
from zope.formlib import form

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.form.validators import null_validator

from plone.app.controlpanel import PloneMessageFactory as _
#from plone.app.users.events import ConfigurationChangedEvent
from plone.app.users.browser.interfaces import IAccountPanelView
from plone.app.users.browser.interfaces import IAccountPanelForm

from plone.protect import CheckAuthenticator


class AccountPanelView(BrowserView):
    """A simple view to be used as a basis for account panel screens."""

    implements(IAccountPanelView)

class AccountPanelForm(FieldsetsEditForm):
    """A simple form to be used as a basis for account panel screens."""

    implements(IAccountPanelForm)
    template = ViewPageTemplateFile('account-panel.pt')

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            self.status = _("Changes saved.")
#            notify(ConfigurationChangedEvent(self, data))
            self._on_save(data)
        else:
            self.status = _("No changes made.")

    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
#        url = getMultiAdapter((self.context, self.request),
#                              name='absolute_url')()
#        self.request.response.redirect(url + '/@@overview-controlpanel')
        return ''
        
    def _on_save(self, data=None):
        pass
