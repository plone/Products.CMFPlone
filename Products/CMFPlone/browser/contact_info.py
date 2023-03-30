# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.browser.interfaces import IContactForm
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.autoform.form import AutoExtensibleForm
from plone.registry.interfaces import IRegistry
from smtplib import SMTPException
from z3c.form import form, button
from zope.component import getUtility
from zope.component.hooks import getSite

import logging
import six

try:
    # Products.MailHost has a patch to fix quoted-printable soft line breaks.
    # See https://github.com/zopefoundation/Products.MailHost/issues/35
    from Products.MailHost.MailHost import message_from_string
except ImportError:
    # If the patch is ever removed, we fall back to the standard library.
    from email import message_from_string


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

    @button.buttonAndHandler(_(u'label_send', default='Send'), name='send')
    def handle_send(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(
                self.formErrorsMessage,
                type=u'error'
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
        if six.PY3:
            message = message.decode(encoding)
        message = message_from_string(message)
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
            message = _(u'Unable to send mail: ${exception}',
                        mapping={u'exception': exception})
            IStatusMessage(self.request).add(message, type=u'error')

    def send_feedback(self):
        IStatusMessage(self.request).add(
            _(u'A mail has now been sent to the site administrator '
              u'regarding your questions and/or comments.')
        )
