from Acquisition import aq_inner
from zope.component import adapts
from zope.interface import implements
from zope.event import notify
from zope.formlib import form

from plone.app.form.validators import null_validator
from plone.app.controlpanel.events import ConfigurationChangedEvent
from plone.fieldsets.form import FieldsetsEditForm
from plone.protect import CheckAuthenticator

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.users.browser.interfaces import IAccountPanelForm, IAccountPanelView

class AccountPanelSchemaAdapter(SchemaAdapterBase):
    adapts(ISiteRoot)

    def __init__(self, context):
        mt = getToolByName(context, 'portal_membership')
        userid = context.REQUEST.get('userid')

        if mt.isAnonymousUser():
            raise "Can't modify properties of anonymous user"
        elif userid:
            self.context = mt.getMemberById(userid)
        else:
            self.context = mt.getAuthenticatedMember()

class AccountPanelView(BrowserView):
    """ The bare view for the account panel is used in the prefs_user_details
    template. This is good enough for now, but it would be better to use a browser
    view for prefs_user_details with a more sophicated solution (no bare views, macro's etc.)
    """
    implements(IAccountPanelView)
    template = ViewPageTemplateFile('account-panel-bare.pt')
    
    def getMacro(self, key):
        return self.template.macros[key]


class AccountPanelForm(FieldsetsEditForm):
    """A simple form to be used as a basis for account panel screens."""

    implements(IAccountPanelForm)
    form_fields = form.FormFields(IAccountPanelForm)
    
    hidden_widgets = []
    prefs_user_details = 'prefs_user_details'

    def render(self):
        """ Default the non-bare temaplte is shown, when a user goes to the personal
        preferences. If an admin accesses the personal preferences of a user thru the
        prefs_user_details the bare template is given.
        """
        if self.request.get(self.prefs_user_details):
            template = ViewPageTemplateFile('account-panel-bare.pt')(self)
        else:
            template = ViewPageTemplateFile('account-panel.pt')(self)
        return template


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

        if self.request.get(self.prefs_user_details):
            self.request.response.redirect('@@usergroup-userprefs')



    @form.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."),
                                                      type="info")

        if self.request.get(self.prefs_user_details):
            self.request.response.redirect('@@usergroup-userprefs')
        else:
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
        
    def _checkPermission(self, permission, context):
        mt = getToolByName(context, 'portal_membership')
        return mt.checkPermission(permission, context)

    def getActionUrl(self):
        if self.request.get(self.prefs_user_details):
            url = self.request.get('page', '@@personal-information')
        else:
            url = self.request.get('URL')

        return url

    def isPrefsUserDetails(self):
        if self.request.get(self.prefs_user_details):
            return True

    def getPersonalInfoLink(self):
        context = aq_inner(self.context)

        template = None
        if self._checkPermission('Set own properties', context):
            if self.request.get(self.prefs_user_details):
                userid = self.request.get('userid')
                template = "%s?userid=%s&page=%s" % (self.prefs_user_details,
                    userid, '@@personal-information')
            else:
                template = '@@personal-information'

        return template

    def getPersonalPrefsLink(self):
        context = aq_inner(self.context)

        template = None
        if self._checkPermission('Set own properties', context):
            if self.request.get(self.prefs_user_details):
                userid = self.request.get('userid')
                template = "%s?userid=%s&page=%s" % (self.prefs_user_details,
                    userid, '@@personal-preferences')
            else:
                template = '@@personal-preferences'

        return template

    def getPasswordLink(self):
        context = aq_inner(self.context)
        
        mt = getToolByName(context, 'portal_membership')
        member = mt.getAuthenticatedMember()

        template = None
        if not self.request.get(self.prefs_user_details) and member.canPasswordSet():
            template = '@@change-password'

        return template