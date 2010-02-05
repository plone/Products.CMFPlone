from zope.interface import implements
from zope.component import getMultiAdapter
from zope.event import notify
from zope.formlib import form

from plone.app.form.validators import null_validator
from plone.app.controlpanel.events import ConfigurationChangedEvent
from plone.fieldsets.form import FieldsetsEditForm
from plone.memoize.view import memoize
from plone.protect import CheckAuthenticator

from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.users.browser.interfaces import IAccountPanelForm



class AccountPanelForm(FieldsetsEditForm):
    """A simple form to be used as a basis for account panel screens."""

    implements(IAccountPanelForm)
    form_fields = form.FormFields(IAccountPanelForm)
    template = ViewPageTemplateFile('account-panel.pt')
    hidden_widgets = []

    @form.action(_(u'label_save', default=u'Save'), name=u'save')
    def handle_edit_action(self, action, data):
        CheckAuthenticator(self.request)
        if form.applyChanges(self.context, self.form_fields, data,
                             self.adapters):
            IStatusMessage(self.request).addStatusMessage(_("Changes saved."),
                                                          type="info")
            notify(ConfigurationChangedEvent(self, data))
            self._on_save(data)
        else:
            IStatusMessage(self.request).addStatusMessage(_("No changes made."),
                                                          type="info")

    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")
        self.request.response.redirect(self.request['ACTUAL_URL'])
        return ''
        
    def _on_save(self, data=None):
        pass


    def showWidget(self, widget):
        """ Hide widgets in the formbase template. 
        """
        widgetName = widget.name.strip('form.')
        if not widgetName in self.hidden_widgets:
            return True