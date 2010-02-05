from Acquisition import aq_parent, aq_inner
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
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from Products.PythonScripts.standard import url_unquote_plus

from plone.app.users.browser.interfaces import IAccountPanelView
from plone.app.users.browser.interfaces import IAccountPanelForm



class AccountPanelView(BrowserView):
    """A simple view to be used as a basis for account panel screens."""

    implements(IAccountPanelView)

    def getAccountTab(self):
        """ Check if the tab exists and return it
        """
        return ""
        context = aq_inner(self.context)
        request = self.request

        account_tab = (len(request.traverse_subpath) > 0 and \
            url_unquote_plus(request.traverse_subpath[0])) or \
            request.get('account_tab', None);

        context_state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        action_list = context_state.actions('accountpanel')
        actions = [action['id'] for action in action_list ]

        defaultTab = None
        if len(actions) > 1:
            defaulTab = actions[0]

        if account_tab in actions:
            return account_tab
        elif not account_tab:
            return defaulTab
        else:
            err_msg =  _(u"The requested account tab was not found.")
            IStatusMessage(self.request).addStatusMessage(err_msg,
                                                          type="error")
            return defaulTab


    
class AccountPanelForm(FieldsetsEditForm):
    """A simple form to be used as a basis for account panel screens."""

    implements(IAccountPanelForm)
    form_fields = form.FormFields(IAccountPanelForm)
    template = ViewPageTemplateFile('account-panel.pt')
    hidden_widgets = []

    @memoize
    def prepareFormTabs(self):
        """Prepare the form tabs ('personal prefs', 'user data', etc..)
        """
        context = aq_inner(self.context)

        context_state = getMultiAdapter((context, self.request), name=u'plone_context_state')
        action_list = context_state.actions('accountpanel')

        tabs = []

        request_url = self.request['ACTUAL_URL']
        selected = context.restrictedTraverse('get_account_tab')()
        
        for action in action_list:
            item = {'title'    : action['title'],
                    'id'       : action['id'],
                    'url'      : action['url'],
                    'selected' : False}

            if action['url'] == request_url:
                item['selected'] = True
            elif action['url'].endswith(selected):
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


    def showWidget(self, widget):
        """ Hide widgets in the formbase template. 
        """
        widgetName = widget.name.strip('form.')
        if not widgetName in self.hidden_widgets:
            return True
            
    def form_action(self):
        context = aq_inner(self.context)
        url = self.request['URL']
        selected = context.restrictedTraverse('get_account_tab')()

        if not url.endswith(selected):
            url = "%s/%s" % (url, selected)
            
        return url
