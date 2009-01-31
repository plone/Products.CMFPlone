#!/usr/bin/env python
# encoding: utf-8
"""
joinform.py
"""

from zope.formlib import form
from zope.app.form.browser import PasswordWidget

from zope.interface import Interface, Invalid
from zope.component import adapts
from zope.interface import implements
from zope import schema
from zope.component import getUtility

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from Products.Five.formlib.formbase import PageForm
from ZODB.POSException import ConflictError

from plone.app.controlpanel import PloneMessageFactory as _


from userdata import IUserDataSchema


class IJoinSchema(Interface):

    username = schema.ASCIILine(title=u'Username',
                               description=u'Unique user name')

    password = schema.TextLine(title=u'Password',
                               description=u'Password')

    password_ctl = schema.TextLine(title=u'Confirm password',
                               description=u'Password')        


class JoinForm(PageForm):

    """ Dynamically get fields from user data, through admin
        config settings.
    """
    
    label = _(u'Join')
    description = _(u"Join the portal.")
    form_name = _(u'Join Form')


    @property
    def form_fields(self):

        portal = getUtility(ISiteRoot)
        props = getToolByName(self.context, 'portal_properties').site_properties
        join_fields = props.getProperty('joinfields')

        all_fields = form.Fields(IUserDataSchema)
        joinpolicy_fields = form.Fields(IJoinSchema)

        fields = form.Fields(*[all_fields[id] for id in join_fields])

        if not portal.getProperty('validate_email', True):

            fields = fields + form.Fields(joinpolicy_fields['username'],
                                          joinpolicy_fields['password'],
                                          joinpolicy_fields['password_ctl'])

            # Can we do this static?
            fields['password'].custom_widget = PasswordWidget
            fields['password_ctl'].custom_widget = PasswordWidget

        else:
            fields = fields + form.Fields(joinpolicy_fields['username'])


        return fields


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
            context.acl_users.userFolderDelUsers([username,], REQUEST=self.request)
            self.status = (_(u'status_fatal_password_mail',
                    default=u'Failed to create your account: we were unable to send your password to your email address: ${address}',
                    mapping={u'address' : data.get('email', '')}))
        else:
            self.status = (_(u'status_nonfatal_password_mail',
                    default=u'You account has been created, but we were unable to send your password to your email address: ${address}',
                    mapping={u'address' : data.get('email', '')}))

        self.request.response.redirect('registered')
