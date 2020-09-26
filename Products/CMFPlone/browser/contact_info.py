from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.browser.interfaces import IContactForm
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from email.mime.text import MIMEText
from plone.autoform.form import AutoExtensibleForm
from plone.registry.interfaces import IRegistry
from smtplib import SMTPException
from z3c.form import form, button
from zope.component import getUtility
from zope.component.hooks import getSite

import logging

log = logging.getLogger(__name__)


class ContactForm(AutoExtensibleForm, form.Form):

    template = ViewPageTemplateFile('templates/contact-info.pt')
    template_mailview = '@@contact-info-email'

    schema = IContactForm
    ignoreContext = True
    success = False

    def mailhost_is_configured(self):
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        if not mail_settings.email_from_address:
            return False
        return True

    @button.buttonAndHandler(_('label_send', default='Send'), name='send')
    def handle_send(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(
                self.formErrorsMessage,
                type='error'
            )

            return

        self.send_message(data)
        self.send_feedback()
        self.success = True

    def generate_mail(self, variables, encoding='utf-8'):
        template = self.context.restrictedTraverse(self.template_mailview)
        return template(self.context, **variables).encode(encoding)

    def send_message(self, data):
        subject = data.get('subject')

        portal = getSite()
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        send_to_address = mail_settings.email_from_address
        from_address = mail_settings.email_from_address
        registry = getUtility(IRegistry)
        encoding = registry.get('plone.email_charset', 'utf-8')
        host = getToolByName(self.context, 'MailHost')

        data['url'] = portal.absolute_url()
        message = self.generate_mail(data, encoding)
        message = MIMEText(message, 'plain', encoding)
        message['Reply-To'] = data['sender_from_address']

        try:
            # This actually sends out the mail
            host.send(
                message,
                send_to_address,
                from_address,
                subject=subject,
                charset=encoding
            )
        except (SMTPException, RuntimeError) as e:
            log.error(e)
            plone_utils = getToolByName(portal, 'plone_utils')
            exception = plone_utils.exceptionString()
            message = _('Unable to send mail: ${exception}',
                        mapping={'exception': exception})
            IStatusMessage(self.request).add(message, type='error')

    def send_feedback(self):
        IStatusMessage(self.request).add(
            _('A mail has now been sent to the site administrator '
              'regarding your questions and/or comments.')
        )
