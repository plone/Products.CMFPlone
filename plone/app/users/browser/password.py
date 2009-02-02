#!/usr/bin/env python
# encoding: utf-8
"""
password.py
"""

from zope.component import getUtility
from zope.interface import implements, Interface
from zope.component import adapts
from zope import schema
from zope.schema import ValidationError
from zope.formlib import form

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.users.browser.form import AccountPanelForm

from plone.app.controlpanel.utils import SchemaAdapterBase
from plone.app.controlpanel import PloneMessageFactory as _
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
        raise CurrentPasswordError()

    return True


class IPasswordSchema(Interface):

    """ Provide schema for password form """

    current_password = schema.Password(title=_(u'label_current_password',
                                                    default=u'Current password'),
                                 description=_(u'help_current_password',
                                                    default=u'Enter your current password.'),
                                 constraint=checkCurrentPassword,
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
    
    label = _(u"Reset Password")
    description = _(u"Change password.")
    form_name = _(u'legend_password_details', default=u'Password Details')
    

    @form.action(_(u'label_change_password', default=u'Change Password'), name=u'reset_passwd')
    def action_reset_passwd(self, action, data):

        portal = getUtility(ISiteRoot)
        registration = portal.portal_registration
        membertool = getToolByName(self.context, 'portal_membership')

        password = data['new_password']
        password_confirm = data['new_password_ctl']

        failMessage = registration.testPasswordValidity(password,
                                                        password_confirm)

        if failMessage:

            IStatusMessage(self.request).addStatusMessage(_(failMessage),
                                                          type="error")
            return

        member = membertool.getAuthenticatedMember()

        try:
            membertool.setPassword(password, None, REQUEST=self.request)
        except AttributeError:
            failMessage=_(u'While changing your password an AttributeError occurred. This is usually caused by your user being defined outside the portal.')

            IStatusMessage(self.request).addStatusMessage(_(failMessage),
                                                          type="error")
            return
        
        IStatusMessage(self.request).addStatusMessage(_("Password changed"),
                                                          type="info")
        return self.request.RESPONSE.redirect('%s/@@personal_preferences' % self.context.absolute_url())
