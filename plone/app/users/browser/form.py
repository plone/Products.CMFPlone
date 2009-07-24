from Acquisition import aq_inner

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.event import notify
from zope.formlib import form

from plone.memoize.view import memoize
from plone.fieldsets.form import FieldsetsEditForm
from plone.app.form.validators import null_validator

from plone.app.controlpanel import PloneMessageFactory as _
from plone.app.controlpanel.events import ConfigurationChangedEvent

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

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

    @memoize
    def prepareFormTabs(self):
        """Prepare the form tabs ('personal prefs', 'user data', etc..)
        """
        context = aq_inner(self.context)

        context_state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        action_list = context_state.actions('accountpanel')

        tabs = []

        request_url = self.request['ACTUAL_URL']

        for action in action_list:
            item = {'title'    : action['title'],
                    'id'       : action['id'],
                    'url'      : action['url'],
                    'selected' : False}

            if action['url'] == request_url:
                item['selected'] = True
            tabs.append(item)

        return tabs

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
