from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import pretty_title_or_id
from Products.CMFPlone.utils import transaction_note
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.MailHost.interfaces import IMailHost
from Products.statusmessages.interfaces import IStatusMessage

from ZODB.POSException import ConflictError

from plone.z3cform import layout

from zope.component import getMultiAdapter
from zope.component import getUtility

from z3c.form import form
from z3c.form import field
from z3c.form import button

from interfaces import ISendToForm


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

    # XXX: Add validation, but the plan is the fields should be
    # changed to the Email field that is to be provided by
    # plone schema

    @button.buttonAndHandler(_(u'label_send', default='Send'),
                             name='send')
    def handle_send(self, action):
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state'
        )
        site = portal_state.portal()

        context_state = getMultiAdapter(
            (self.context, self.request),
            "plone_context_state"
        )
        url = context_state.view_url()

        send_from_address = self.request.get('send_from_address')
        send_to_address = self.request.get('send_to_address')
        subject = pretty_title_or_id(self.context)
        title = pretty_title_or_id(self.context)
        description = self.context.Description()
        comment = self.request.get('comment', None)
        envelope_from = site.getProperty('email_from_address', None)

        try:
            # Sends a link of a page to someone.
            host = getUtility(IMailHost)
            encoding = site.getProperty('email_charset')

            if not envelope_from:
                envelope_from = send_from_address

            # Cook from template
            message = self.template(
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
        except:
            # TODO To many things could possibly go wrong. So we catch all.
            IStatusMessage(self.request).addStatusMessage(
                _(u'Unable to send mail.'),
                type=u'error'
            )
            return

        transaction_note(
            'Sent page %s to %s' % (url, send_to_address)
        )

        IStatusMessage(self.request).addPortalMessage(
            _(u'Mail sent.'),
            type=u'info'
        )

send_to_form = layout.wrap_form(SendToForm)
