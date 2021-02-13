from email import message_from_string
from email.header import Header
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ILoginHelpForm
from Products.CMFPlone.interfaces import ILoginHelpFormSchema
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from smtplib import SMTPException
from smtplib import SMTPRecipientsRefused
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.interface import implementer

import logging


SEND_USERNAME_TEMPLATE = _("mailtemplate_username_info", default="""From: {encoded_mail_sender}
To: {email}
Subject: Your username for {portal_url}
Content-Type: text/plain
Precedence: bulk

Dear {fullname},

You requested to be reminded of your username for {portal_url}.
Your username is: {login}


With kind regards,

--

{email_from_name}""")

log = logging.getLogger(__name__)


class RequestResetPassword(form.Form):

    id = 'RequestResetPassword'
    label = ''
    fields = field.Fields(ILoginHelpFormSchema).select('reset_password')
    ignoreContext = True

    render = ViewPageTemplateFile('templates/subform_render.pt')

    def updateActions(self):
        super(RequestResetPassword, self).updateActions()
        self.actions['reset'].addClass('btn-primary')

    def updateWidgets(self):
        super().updateWidgets()
        if self.use_email_as_login():
            self.widgets['reset_password'].label = _(
                'label_email',
                default='Email'
            )

    @button.buttonAndHandler(
        _('button_pwreset_reset_password', default='Reset your password'),
        name='reset'
    )
    def handleResetPassword(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        portal = getSite()
        regtool = getToolByName(portal, 'portal_registration')
        try:
            regtool.mailPassword(data['reset_password'], self.request)
        except ValueError as e:
            # Paranoia Warning!
            # We act as if a message has been sent to prevent probing Plone
            # for valid loginnames. Instead we log the error-message.
            log.info('Error while trying to send a reset-password notice to user {}: {}'.format(data['reset_password'], e))  # noqa: E501
            pass

        IStatusMessage(self.request).addStatusMessage(
            _('statusmessage_pwreset_password_mail_sent', default='An '
              'email has been sent with instructions on how to reset your '
              'password.'), 'info')

    def use_email_as_login(self):
        registry = getUtility(IRegistry)
        security_settings = registry.forInterface(
            ISecuritySchema, prefix='plone')
        return security_settings.use_email_as_login


class RequestUsername(form.Form):

    id = 'RequestUsername'
    label = ''
    fields = field.Fields(ILoginHelpFormSchema).select('recover_username')
    ignoreContext = True

    render = ViewPageTemplateFile('templates/subform_render.pt')

    def updateActions(self):
        super(RequestUsername, self).updateActions()
        self.actions['get_username'].addClass('btn-primary')

    @button.buttonAndHandler(
        _('button_pwreset_get_username', default='Get your username'),
        name='get_username'
    )
    def handleGetUsername(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        portal = getSite()
        pas = getToolByName(portal, 'acl_users')
        email = data['recover_username']
        results = pas.searchUsers(email=email, exact_match=True)
        send_email = True
        if not results:
            log.info(f'No user found for {email}')
            send_email = False
        if len(results) > 1:
            log.info(f'More than one user found for {email}')
            send_email = False
        if send_email:
            self.send_username(portal, results[0])

        # Paranoia Warning!
        # Same as with the reset-password form we don't want to allow
        # probing for email-adresses of existing users.
        # Because of this we always act as if that an email has been sent.
        # Instead we log the error-message.
        IStatusMessage(self.request).addStatusMessage(
            _('statusmessage_pwreset_username_mail_sent',
                default='An email has been sent with your username.'),
            'info'
        )

    def send_username(self, portal, userinfo):
        registry = getUtility(IRegistry)
        encoding = registry.get('plone.email_charset', 'utf-8')
        translated_template = translate(
            SEND_USERNAME_TEMPLATE,
            context=self.request,
        )

        mail_text = translated_template.format(
            email=userinfo['email'],
            portal_url=portal.absolute_url(),
            fullname=userinfo['title'],
            login=userinfo['login'],
            email_from_name=registry['plone.email_from_name'],
            encoded_mail_sender=self.encoded_mail_sender(),
        )
        message_obj = message_from_string(mail_text.strip())
        subject = message_obj['Subject']
        m_to = message_obj['To']
        m_from = message_obj['From']
        msg_type = message_obj.get('Content-Type', 'text/plain')

        host = getToolByName(portal, 'MailHost')
        try:
            host.send(mail_text, m_to, m_from, subject=subject,
                      charset=encoding, immediate=True,
                      msg_type=msg_type)
        except SMTPRecipientsRefused:
            # Don't disclose email address on failure
            raise SMTPRecipientsRefused(
                _('Recipient address rejected by server.'))
        except SMTPException as e:
            raise(e)

    def encode_mail_header(self, text):
        """ Encodes text into correctly encoded email header """
        return Header(safe_unicode(text), 'utf-8')

    def encoded_mail_sender(self):
        """ returns encoded version of Portal name <portal_email> """
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        from_ = mail_settings.email_from_name
        mail = mail_settings.email_from_address
        return '"{}" <{}>'.format(self.encode_mail_header(from_), mail)


@implementer(ILoginHelpForm)
class LoginHelpForm(form.EditForm):
    ''' Implementation of the login help form '''

    subforms = []

    id = 'LoginHelpForm'
    label = _('heading_login_form_help', default='Need Help?')

    ignoreContext = True

    def render(self):
        return self.index()

    def can_reset_password(self):
        # TODO: Actually check that the site allows reseting password
        return True

    def can_retrieve_username(self):
        # TODO: Actually check that the site allows retrieving the username
        return True

    def update(self):
        subforms = []
        # XXX: Not really sure how to handle the action and enctype vars
        if self.can_reset_password():
            form = RequestResetPassword(None, self.request)
            form.update()
            subforms.append(form)
        if not self.use_email_as_login() and self.can_retrieve_username():
            form = RequestUsername(None, self.request)
            form.update()
            subforms.append(form)

        self.subforms = subforms
        super().update()

    def use_email_as_login(self):
        registry = getUtility(IRegistry)
        security_settings = registry.forInterface(
            ISecuritySchema, prefix='plone')
        return security_settings.use_email_as_login
