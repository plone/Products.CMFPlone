from Acquisition import aq_inner

from zope.component import getUtility
from zope.component import adapts
from zope.interface import implements, Interface
from zope import schema
from zope.app.form.interfaces import WidgetInputError
from zope.app.form.browser import DropdownWidget
from zope.schema import ValidationError
from zope.schema import Choice
from zope.schema import Bool
from zope.formlib import form

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.users.browser.account import AccountPanelForm, AccountPanelSchemaAdapter
from plone.app.users.userdataschema import IUserDataSchema
from plone.app.users.userdataschema import IUserDataSchemaProvider

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.widgets import FileUploadWidget
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import set_own_login_name
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

class IPersonalPreferences(Interface):

    """ Provide schema for personalize form """

    wysiwyg_editor = Choice(
        title=u'Wysiwyg editor',
        description=u'Wysiwyg editor to use.',
        vocabulary="plone.app.vocabularies.AvailableEditors",
        required=False,
        )

    ext_editor = Bool(
        title=_(u'label_ext_editor', default=u'Enable external editing'),
        description=u'When checked, an option will be '
           'made visible on each page which allows you '
           'to edit content with your favorite editor '
           'instead of using browser-based editors. This '
           'requires an additional application, most often '
           'ExternalEditor or ZopeEditManager, installed '
           'client-side. Ask your administrator for more '
           'information if needed.',
        )
    
    listed = Bool(
        title=_(u'label_listed_status', default=u'Listed in searches'),
        description=u'Determines if your user name is listed in user '
                    'searches done on this site.',
        required=False
        )

    visible_ids = Bool(
        title=_(u'label_edit_short_names', 
            default=u'Allow editing of Short Names'),
        description=u'Determines if Short Names (also known '
               'as IDs) are changable when editing items. If Short '
               'Names are not displayed, they will be generated automatically.',
        required=False
           )
        
    language = Choice(
        title=_(u'label_language', default=u'Language'),
        description=_(u'help_preferred_language', u'Your preferred language.'),
        vocabulary="plone.app.vocabularies.AvailableContentLanguages",
        required=False
        )

class PersonalPreferencesPanelAdapter(AccountPanelSchemaAdapter):

    def get_wysiwyg_editor(self):
        return self.context.getProperty('wysiwyg_editor', '')

    def set_wysiwyg_editor(self, value):
        # No value means "use site default", portal_memberdata expects an empty string, not a None. 
        # (As opposed to "None" which means "no editor")
        if value is None:
            value = ''
        return self.context.setMemberProperties({'wysiwyg_editor': value})

    wysiwyg_editor = property(get_wysiwyg_editor, set_wysiwyg_editor)


    def get_ext_editor(self):
        return self.context.getProperty('ext_editor', '')

    def set_ext_editor(self, value):
        return self.context.setMemberProperties({'ext_editor': value})

    ext_editor = property(get_ext_editor, set_ext_editor)
 
 
    def get_listed(self):
        return self.context.getProperty('listed', '')

    def set_listed(self, value):
        return self.context.setMemberProperties({'listed': value})

    listed = property(get_listed, set_listed)
    
    
    def get_visible_ids(self):
        return self.context.getProperty('visible_ids', '')

    def set_visible_ids(self, value):
        return self.context.setMemberProperties({'visible_ids': value})

    visible_ids = property(get_visible_ids, set_visible_ids)


    def get_language(self):
        return self.context.getProperty('language', '')

    def set_language(self, value):
        return self.context.setMemberProperties({'language': value})

    language = property(get_language, set_language)


def LanguageWidget(field, request):

    """ Create selector with languages vocab """
    
    widget = DropdownWidget(field, field.vocabulary, request)
    widget._messageNoValue = _(u"vocabulary-missing-single-value-for-edit",
                        u"Language neutral (site default)")
    return widget


def WysiwygEditorWidget(field, request):

    """ Create selector with available editors """

    widget = DropdownWidget(field, field.vocabulary, request)
    widget._messageNoValue = _(u"vocabulary-available-editor-novalue",
                        u"Use site default")
    return widget

class PersonalPreferencesPanel(AccountPanelForm):
    """ Implementation of personalize form that uses formlib """

    label = _(u"heading_my_preferences", default=u"Personal Preferences")
    description = _(u"description_my_preferences", default=u"Your personal settings.")
    form_name = _(u'legend_personal_details', u'Personal Details')

    form_fields = form.FormFields(IPersonalPreferences)
    form_fields['language'].custom_widget = LanguageWidget
    form_fields['wysiwyg_editor'].custom_widget = WysiwygEditorWidget 
    

    def setUpWidgets(self, ignore_request=False):
        """ Hide the visible_ids field based on portal_properties.
        """
        context = aq_inner(self.context)
        properties = getToolByName(context, 'portal_properties')
        siteProperties = properties.site_properties
        
        if not siteProperties.visible_ids:
            self.hidden_widgets.append('visible_ids')
        
        super(PersonalPreferencesPanel, self).setUpWidgets(ignore_request)

class PersonalPreferencesConfiglet(PersonalPreferencesPanel):
    """ """
    template = ViewPageTemplateFile('account-configlet.pt')


class UserDataPanelAdapter(AccountPanelSchemaAdapter):

    def _getProperty(self, name):
        """ PlonePAS encodes all unicode coming from PropertySheets. 
            Decode before sending to formlib. """
        value = self.context.getProperty(name, '')
        if value:
            return value.decode('utf-8')
        return value
        
    def get_fullname(self):
        return self._getProperty('fullname')

    def set_fullname(self, value):
        return self.context.setMemberProperties({'fullname': value})

    fullname = property(get_fullname, set_fullname)

    def get_email(self):
        return self._getProperty('email')

    def set_email(self, value):
        props = getToolByName(self, 'portal_properties').site_properties
        if props.getProperty('use_email_as_login'):
            set_own_login_name(self.context, value)
        return self.context.setMemberProperties({'email': value})

    email = property(get_email, set_email)


    def get_home_page(self):
        return self._getProperty('home_page')

    def set_home_page(self, value):
        return self.context.setMemberProperties({'home_page': value})

    home_page = property(get_home_page, set_home_page)


    def get_description(self):
        return self._getProperty('description')

    def set_description(self, value):
        return self.context.setMemberProperties({'description': value})
        
    description = property(get_description, set_description)
    
    
    def get_location(self):
        return self._getProperty('location')

    def set_location(self, value):
        return self.context.setMemberProperties({'location': value})

    location = property(get_location, set_location)

    def get_portrait(self):
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        portrait = mtool.getPersonalPortrait(member.id)
        return portrait

    def set_portrait(self, value):
        if value:
            context = aq_inner(self.context)
            context.portal_membership.changeMemberPortrait(value)

    portrait = property(get_portrait, set_portrait)

    def get_pdelete(self):
        pass

    def set_pdelete(self, value):
        if value:
            context = aq_inner(self.context)
            context.portal_membership.deletePersonalPortrait()

    pdelete = property(get_pdelete, set_pdelete)
    
class UserDataPanel(AccountPanelForm):

    label = _(u'title_personal_information_form', default=u'Personal Information')
    description = _(u'description_personal_information_form', default='Change your personal information')
    form_name = _(u'User Data Form')

    def __init__(self, context, request):
        """ Load the UserDataSchema at view time. 
        
        (Because doing getUtility for IUserDataSchemaProvider fails at startup
        time.)
   
        """
        super(UserDataPanel, self).__init__(context, request)
        util = getUtility(IUserDataSchemaProvider)
        schema = util.getSchema()
        self.form_fields = form.FormFields(schema)
        self.form_fields['portrait'].custom_widget = FileUploadWidget

    def getPortrait(self):
        context = aq_inner(self.context)
        return context.portal_membership.getPersonalPortrait()

class UserDataConfiglet(UserDataPanel):
    """ """
    template = ViewPageTemplateFile('account-configlet.pt')


class CurrentPasswordError(ValidationError):
    __doc__ = _(u"Incorrect value for current password")


# Define validator(s)
#
def checkCurrentPassword(value):

    """ Test current password against given. """

    portal = getUtility(ISiteRoot)
    membertool = getToolByName(portal, 'portal_membership')

    current_password = value.encode('ascii', 'ignore')

    if not membertool.testCurrentPassword(current_password):
        raise  ()

    return True
    
class IPasswordSchema(Interface):

    """ Provide schema for password form """

    current_password = schema.Password(title=_(u'label_current_password',
                                                    default=u'Current password'),
                                 description=_(u'help_current_password',
                                                    default=u'Enter your current password.'),
                                 #constraint=checkCurrentPassword,
                                       )

    new_password = schema.Password(title=_(u'label_new_password', default=u'New password'),
                                   description=_(u'help_new_password',
                                                    default=u"Enter your new password. "
                                                             "Minimum 5 characters."),
                                   )

    new_password_ctl = schema.Password(title=_(u'label_confirm_password', default=u'Confirm password'),
                                 description=_(u'help_confirm_password',
                                                    default=u"Re-enter the password. "
                                                            "Make sure the passwords are identical."),
                                       )



class PasswordPanelAdapter(SchemaAdapterBase):

    adapts(ISiteRoot)
    implements(IPasswordSchema)

    def __init__(self, context):

        self.context = getToolByName(context, 'portal_membership')

        
    def get_dummy(self):

        """ We don't actually need to 'get' anything ..."""
        
        return ''


    current_password = property(get_dummy)

    new_password = property(get_dummy)

    new_password_ctl = property(get_dummy)


class PasswordAccountPanel(AccountPanelForm):
    
    """ Implementation of password reset form that uses formlib"""

    form_fields = form.FormFields(IPasswordSchema)
    
    label = _(u'listingheader_reset_password', default=u'Reset Password')
    description = _(u"Change Password")
    form_name = _(u'legend_password_details', default=u'Password Details')

    def validate_password(self, action, data):
        context = aq_inner(self.context)
        registration = getToolByName(context, 'portal_registration')
        membertool = getToolByName(context, 'portal_membership')

        errors = super(PasswordAccountPanel, self).validate(action, data)

        # check if password is correct
        current_password = data.get('current_password')
        if current_password:
            current_password = current_password.encode('ascii', 'ignore')
            
            if not membertool.testCurrentPassword(current_password):
                err_str = _(u"Incorrect value for current password")
                errors.append(WidgetInputError('current_password',
                                  u'label_current_password', err_str))
                self.widgets['current_password'].error = err_str


        # check if passwords are same and minimum length of 5 chars
        new_password = data.get('new_password')
        new_password_ctl = data.get('new_password_ctl')
        if new_password and new_password_ctl:
            failMessage = registration.testPasswordValidity(new_password,
                                                            new_password_ctl)
            if failMessage:
                errors.append(WidgetInputError('new_password',
                                  u'label_new_password', failMessage))
                errors.append(WidgetInputError('new_password_ctl',
                                  u'new_password_ctl', failMessage))
                self.widgets['new_password'].error = failMessage
                self.widgets['new_password_ctl'].error = failMessage
        
        return errors
    
    @form.action(_(u'label_change_password', default=u'Change Password') ,validator='validate_password', name=u'reset_passwd')
    def action_reset_passwd(self, action, data):
        membertool = getToolByName(self.context, 'portal_membership')

        password = data['new_password']

        try:
            membertool.setPassword(password, None, REQUEST=self.request)
        except AttributeError:
            failMessage=_(u'While changing your password an AttributeError occurred. This is usually caused by your user being defined outside the portal.')

            IStatusMessage(self.request).addStatusMessage(_(failMessage),
                                                          type="error")
            return

        IStatusMessage(self.request).addStatusMessage(_("Password changed"),
                                                          type="info")
