#!/usr/bin/env python
# encoding: utf-8
"""
joinform.py
"""


from zope.interface import Interface, Invalid
from zope.component import getUtility

from zope import schema
from zope.formlib import form
from zope.app.form.browser import TextWidget, CheckBoxWidget

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from Products.Five.formlib.formbase import PageForm
from ZODB.POSException import ConflictError

from plone.app.controlpanel import PloneMessageFactory as _


from userdata import IUserDataSchema


# Define constants from the Join schema that should be added to the
# vocab of the join fields setting in usergroupssettings controlpanel.
JOIN_CONST = ['username', 'password', 'mail_me']

class IJoinSchema(Interface):

    username = schema.ASCIILine(title=_(u'User Name'),
                               description=_(u"""
                               Enter a user name, usually something like
                               'jsmith'.
                               No spaces or special characters.
                               Usernames and passwords are case sensitive,
                               make sure the caps lock key is not enabled.
                               This is the name used to log in."""))

    password = schema.Password(title=_(u'Password'),
                               description=_(u'Minimum 5 characters.'))

    password_ctl = schema.Password(title=_(u'Confirm password'),
                               description=_(u"""
                               Re-enter the password.
                               Make sure the passwords are identical."""))

    mail_me = schema.Bool(title=_(u"Send a mail with the password"),
                          default=False)

def FullNameWidget(field, request):

    """ Change the description of the widget """
    
    field.description = _(u"Enter full name, eg. John Smith.")
    widget = TextWidget(field, request)
    return widget

def EmailWidget(field, request):

    """ Change the description of the widget """
    
    field.description = _(u"""
                    Enter an email address.
                    This is necessary in case the password is lost.
                    We respect your privacy, and will not give the address
                    away to any third parties or expose it anywhere.""")
    widget = TextWidget(field, request)
    return widget

#from zope.app.form.browser.widget import DisplayWidget
class NoDisplayWidget(CheckBoxWidget):
    """A 'no display' widget used for info messages.
    """    
    type = 'nodisplay'
    default = 0
    extra = ''

    def __init__(self, context, request):
        super(NoDisplayWidget, self).__init__(context, request)
        self.required = False

    def __call__(self):
        """Render the widget to HTML."""
        return ""

def CantChoosePasswordWidget(field, request):

    """ Change the widget """
    
    field.title = u''
    field.readonly = True
    field.description = _(u"""
                    A URL will be generated and e-mailed to you;
                    follow the link to reach a page where you can change your
                    password and complete the registration process.""")
    widget = NoDisplayWidget(field, request)
    return widget

class JoinForm(PageForm):

    """ Dynamically get fields from user data, through admin
        config settings.
    """
    
    label = _(u'Join')
    description = _(u"Join the portal.")
    form_name = _(u'Join Form')


    @property
    def form_fields(self):

        """ form_fields is dynamic in this form, to be able to handle
        different join styles.
        """

        portal = getUtility(ISiteRoot)
        props = getToolByName(self.context, 'portal_properties').site_properties
        join_fields = list(props.getProperty('join_form_fields'))

        canSetOwnPassword = not portal.getProperty('validate_email', True)
        

        # Check on required join fields
        #
        if not 'username' in join_fields:

            join_fields.insert(0, 'username')

        if canSetOwnPassword:
            # Add password if needed
            #
            if not 'password' in join_fields:
                
                join_fields.insert(join_fields.index('username') + 1,
                                   'password')

            # Add password_ctl after password
            #
            if not 'password_ctl' in join_fields:
                
                join_fields.insert(join_fields.index('password') + 1,
                                   'password_ctl')

            # Add email_me after password_ctl
            #
            if not 'mail_me' in join_fields:
                
                join_fields.insert(join_fields.index('password_ctl') + 1,
                                   'mail_me')

        # Can the user actually set his/her own password? If not, skip
        # password fields in final list.
        #
        if not canSetOwnPassword:
            if 'password' in join_fields:
                del join_fields[join_fields.index('password')]
            if 'password_ctl' in join_fields:
                del join_fields[join_fields.index('password_ctl')]

        # We need fields from both schemata here.
        #
        all_fields = form.Fields(IUserDataSchema) + form.Fields(IJoinSchema)
        all_fields['fullname'].custom_widget = FullNameWidget
        all_fields['email'].custom_widget = EmailWidget
        if portal.validate_email:
            all_fields['mail_me'].custom_widget = CantChoosePasswordWidget


        # Pass the list of join form fields as a reference to the
        # Fields constructor, and return.
        #
        return form.Fields(*[all_fields[id] for id in join_fields])


    @form.action("join")
    def action_join(self, action, data):
        
        portal = getUtility(ISiteRoot)
        registration = portal.portal_registration

        username = data['username']

        password = data.get('password') or registration.generatePassword()

        try:
            registration.addMember(username, password, properties=data, REQUEST=self.request)
        except AttributeError:
            raise Invalid(_(u'The login name you selected is already in use or is not valid. Please choose another.'))

        if portal.validate_email or self.request.get('mail_me', 0):
            try:
                registration.registeredNotify(username)
            except ConflictError:
                raise Invalid(_(u'Argh'))
            except Exception:
                raise Invalid(_(u'Argh 2'))

        if portal.validate_email:
            self.context.acl_users.userFolderDelUsers([username,], REQUEST=self.request)
            self.status = (_(u'status_fatal_password_mail',
                    default=u'Failed to create your account: we were unable to send your password to your email address: ${address}',
                    mapping={u'address' : data.get('email', '')}))
        else:
            self.status = (_(u'status_nonfatal_password_mail',
                    default=u'You account has been created, but we were unable to send your password to your email address: ${address}',
                    mapping={u'address' : data.get('email', '')}))

        self.request.response.redirect('registered')
