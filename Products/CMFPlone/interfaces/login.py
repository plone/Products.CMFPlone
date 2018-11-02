# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from plone.schema.email import Email
from plone.z3cform.interfaces import IWrappedForm
from zope import schema
from zope.interface import Interface


class IRedirectAfterLogin(Interface):
    """ Redirect after login adapters should provide this interface """


class IForcePasswordChange(Interface):
    """ Hook point to customize forcing a password change """


class IInitialLogin(Interface):
    """ Hook point to customize what happens the first time a user logs into
        the site """


class ILogin(Interface):
    """ Login form schema """

    login = schema.TextLine(
        title=_(u'label_log_in', default=u'Log in'),
    )

    password = schema.Password(
        title=_(u'label_password', default=u'Password'),
    )


class ILoginForm(IWrappedForm):
    """ Login form marker interface """


class ILoginFormSchema(Interface):
    """ Login form schema """

    ac_name = schema.TextLine(
        title=_(u'label_login_name', default=u'Login Name'),
        required=True,
    )

    ac_password = schema.Password(
        title=_(u'label_password', default=u'Password'),
        required=True,
    )

    came_from = schema.TextLine(
        title=u'Came From',  # not translated, hidden field
        required=False,
    )


class ILoginHelpForm(IWrappedForm):
    """ Login Help form marker interface """


class ILoginHelpFormSchema(Interface):
    """ Login Help form schema """

    reset_password = schema.TextLine(
        title=_(u'label_pwreset_username', default=u'Username'),
        description=_(
            u'help_pwreset_username',
            default=u'Enter your username '
                    u'or email and we’ll send you a password reset link.',
        ),
        required=True,
    )

    recover_username = Email(
        title=_(u'label_pwreset_email', default=u'Email'),
        description=_(
            u'help_pwreset_email',
            default=u'Enter your email and '
                    u'we’ll send you your username.',
        ),
        required=True,
    )
