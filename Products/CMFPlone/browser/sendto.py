from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.utils import pretty_title_or_id
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MailHost.interfaces import IMailHost
from Products.statusmessages.interfaces import IStatusMessage

from ZODB.POSException import ConflictError

from plone.registry.interfaces import IRegistry
from plone.z3cform import layout

from zope.component import getMultiAdapter
from zope.component import getUtility

from z3c.form import form
from z3c.form import field
from z3c.form import button

from interfaces import ISendToForm

import logging

logger = logging.getLogger("Plone")


class SendToForm(form.Form):
    label = _(u'heading_send_page_to',
              default=u'Send this page to someone')

    description = _(u'description_send_page_url_to',
                    default=u'Fill in the email address of your '
                    u'friend, and we will send an email '
                    u'that contains a link to this page.')

    fields = field.Fields(ISendToForm)
    ignoreContext = True

    mail_template = ViewPageTemplateFile('templates/sendto_template.pt')

    @button.buttonAndHandler(_(u'label_send', default='Send'),
                             name='send')
    def handle_send(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).addStatusMessage(
                self.formErrorsMessage,
                type=u'error'
            )
            return

        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )
        site = portal_state.portal()

        context_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_context_state'
        )
        url = context_state.view_url()

        send_from_address = data.get('send_from_address')
        send_to_address = data.get('send_to_address')
        subject = pretty_title_or_id(self, self.context)
        title = pretty_title_or_id(self, self.context)
        description = self.context.Description()
        comment = data.get('comment', None)
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        envelope_from = mail_settings.email_from_address

        try:
            # Sends a link of a page to someone.
            host = getUtility(IMailHost)
            registry = getUtility(IRegistry)
            encoding = registry.get('plone.email_charset', 'utf-8')

            if not envelope_from:
                envelope_from = send_from_address

            # Cook from template
            message = self.mail_template(
                self,
                send_to_address=send_to_address,
                send_from_address=send_from_address,
                comment=comment,
                subject=subject,
                title=title,
                description=description
            )

            message = message.encode(encoding)

            host.send(
                message,
                mto=send_to_address,
                mfrom=envelope_from,
                subject=subject,
                charset='utf-8'
            )

        except ConflictError:
            raise
        except Exception as e:
            # TODO To many things could possibly go wrong. So we catch all.
            logger.info("Unable to send mail: " + str(e))
            IStatusMessage(self.request).addStatusMessage(
                _(u'Unable to send mail.'),
                type=u'error'
            )
            return

        IStatusMessage(self.request).addStatusMessage(
            _(u'Mail sent.'),
            type=u'info'
        )

send_to_form = layout.wrap_form(SendToForm)
