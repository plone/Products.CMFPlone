from Acquisition import aq_inner
from zope.component import adapts
from zope.interface import implements
from zope.event import notify
from zope.formlib import form
from ZTUtils import make_query

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
    """ The bare view for the account panel with macro function.
    """
    implements(IAccountPanelView)
    template = ViewPageTemplateFile('account-panel-bare.pt')

    def getMacro(self, key):
        return self.template.macros[key]


class AccountPanelForm(FieldsetsEditForm):
    """A simple form to be used as a basis for account panel screens."""

    implements(IAccountPanelForm)
    form_fields = form.FormFields(IAccountPanelForm)
    template = ViewPageTemplateFile('account-panel.pt')

    hidden_widgets = []

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.userid = self.request.get('userid')

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

    def makeQuery(self, **kw):
        return make_query(**kw)

    def showWidget(self, widget):
        """ Hide widgets in the formbase template. 
        """
        widgetName = widget.name.strip('form.')
        if not widgetName in self.hidden_widgets:
            return True
        
    def _checkPermission(self, permission, context):
        mt = getToolByName(context, 'portal_membership')
        return mt.checkPermission(permission, context)

    def getPersonalInfoLink(self):
        context = aq_inner(self.context)

        template = None
        if self._checkPermission('Set own properties', context):
            template = '@@personal-information'

        return template

    def getPersonalPrefsLink(self):
        context = aq_inner(self.context)

        template = None
        if self._checkPermission('Set own properties', context):
            template = '@@personal-preferences'

        return template

    def getPasswordLink(self):
        context = aq_inner(self.context)
        
        mt = getToolByName(context, 'portal_membership')
        member = mt.getAuthenticatedMember()

        template = None
        if member.canPasswordSet():
            template = '@@change-password'

        return template
