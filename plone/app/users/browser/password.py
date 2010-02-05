from Acquisition import aq_inner

from zope.component import getUtility
from zope.interface import implements, Interface
from zope.component import adapts
from zope import schema
from zope.app.form.interfaces import WidgetInputError
from zope.schema import ValidationError
from zope.formlib import form

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.users.browser.account import AccountPanelForm

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage


class CurrentPasswordError(ValidationError):
    __doc__ = _(u"Incorrect password",
                default=u"Incorrect value for current password")


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
            print failMessage
            if failMessage:
                errors.append(WidgetInputError('new_password',
                                  u'label_new_password', failMessage))
                errors.append(WidgetInputError('new_password_ctl',
                                  u'new_password_ctl', failMessage))
                self.widgets['new_password'].error = failMessage
                self.widgets['new_password_ctl'].error = failMessag
        
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
