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
        title=_('label_log_in', default='Log in'),
    )

    password = schema.Password(
        title=_('label_password', default='Password'),
    )


class ILoginForm(IWrappedForm):
    """ Login form marker interface """


class ILoginFormSchema(Interface):
    """ Login form schema """

    ac_name = schema.TextLine(
        title=_('label_login_name', default='Login Name'),
        required=True,
    )

    ac_password = schema.Password(
        title=_('label_password', default='Password'),
        required=True,
    )

    came_from = schema.TextLine(
        title='Came From',  # not translated, hidden field
        required=False,
    )


class ILoginHelpForm(IWrappedForm):
    """ Login Help form marker interface """


class ILoginHelpFormSchema(Interface):
    """ Login Help form schema """

    reset_password = schema.TextLine(
        title=_('label_pwreset_username', default='Username'),
        description=_(
            'help_pwreset_username',
            default='Enter your username '
                    'or email and we’ll send you a password reset link.',
        ),
        required=True,
    )

    recover_username = Email(
        title=_('label_pwreset_email', default='Email'),
        description=_(
            'help_pwreset_email',
            default='Enter your email and '
                    'we’ll send you your username.',
        ),
        required=True,
    )
