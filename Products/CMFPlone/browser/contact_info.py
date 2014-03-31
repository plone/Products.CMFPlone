import logging
from smtplib import SMTPException

from zope.site.hooks import getSite
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.browser.interfaces import IContactForm
from z3c.form import form, field, button

log = logging.getLogger(__name__)


class ContactForm(form.Form):

    template = ViewPageTemplateFile(
        'templates/contact-info.pt'
    )

    fields = field.Fields(IContactForm)
    ignoreContext = True

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
        return

    def send_message(self, data):
        context = self.context

        sender_from_address = data.get('sender_from_address')
        sender_fullname = data.get('sender_fullname')
        subject = data.get('subject')
        message = data.get('message')

        portal = getSite()
        send_to_address = portal.getProperty('email_from_address')
        from_address = portal.getProperty('email_from_address')
        encoding = portal.getProperty('email_charset')
        host = getToolByName(self.context, 'MailHost')

        url = portal.absolute_url()

        variables = {
            'sender_from_address': sender_from_address,
            'sender_fullname': sender_fullname,
            'url': url,
            'subject': subject,
            'message': message,
        }

        try:
            message = context.restrictedTraverse('@@contact-info-email')(
                context, **variables)
            message = message.encode(encoding)
            host.send(message, send_to_address, from_address, subject=subject,
                      charset=encoding)
        except (SMTPException, RuntimeError), e:
            log.error(e)
            plone_utils = getToolByName(context, 'plone_utils')
            exception = plone_utils.exceptionString()
            message = _(u'Unable to send mail: ${exception}',
                        mapping={u'exception': exception})
            IStatusMessage(self.request).add(message, type=u'error')
            return

        return

    def send_feedback(self):
        IStatusMessage(self.request).add(
            _(u'A mail has now been sent to the site administrator '
              'regarding your questions and/or comments.')
        )
        return
