from plone.autoform.form import AutoExtensibleForm
from plone.base import PloneMessageFactory as _
from plone.base.interfaces.controlpanel import IMailSchema
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import IContactForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from smtplib import SMTPException
from z3c.form import button
from z3c.form import form
from zope.component import getUtility
from zope.component.hooks import getSite

import logging
import warnings


try:
    # Products.MailHost has a patch to fix quoted-printable soft line breaks.
    # See https://github.com/zopefoundation/Products.MailHost/issues/35
    from Products.MailHost.MailHost import message_from_string
except ImportError:
    # If the patch is ever removed, we fall back to the standard library.
    from email import message_from_string


log = logging.getLogger(__name__)


class ContactForm(AutoExtensibleForm, form.Form):
    template = ViewPageTemplateFile("templates/contact-info.pt")
    template_mailview = "@@contact-info-email"

    schema = IContactForm
    ignoreContext = True
    success = False

    def mailhost_is_configured(self):
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        if not mail_settings.email_from_address:
            return False
        return True

    @button.buttonAndHandler(_("label_send", default="Send"), name="send")
    def handle_send(self, action):
        data, errors = self.extractData()
        if errors:
            IStatusMessage(self.request).add(self.formErrorsMessage, type="error")

            return

        self.send_message(data)
        self.send_feedback()
        self.success = True

    def generate_mail(self, variables, encoding=None):
        template = self.context.restrictedTraverse(self.template_mailview)
        result = template(self.context, **variables)
        if encoding is not None:
            # Maybe someone has customized 'send_message'
            # and still expects to get an encoded answer back.
            warnings.warn(
                "Calling generate_mail with an encoding argument is deprecated. "
                "You can leave it out, and get text (string) as result.",
                DeprecationWarning,
            )
            result = result.encode(encoding)
        return result

    def send_message(self, data):
        subject = data.get("subject")

        portal = getSite()
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        send_to_address = mail_settings.email_from_address
        from_address = mail_settings.email_from_address
        registry = getUtility(IRegistry)
        encoding = registry.get("plone.email_charset", "utf-8")
        host = getToolByName(self.context, "MailHost")

        data["url"] = portal.absolute_url()
        message = self.generate_mail(data)
        if isinstance(message, bytes):
            # Maybe someone has customized 'generate_mail'
            # and still handles the encoding keyword argument.
            message = message.decode(encoding)
        message = message_from_string(message)
        message["Reply-To"] = data["sender_from_address"]

        try:
            # This actually sends out the mail
            host.send(
                message,
                send_to_address,
                from_address,
                subject=subject,
                charset=encoding,
            )
        except (SMTPException, RuntimeError) as e:
            log.error(e)
            plone_utils = getToolByName(portal, "plone_utils")
            exception = plone_utils.exceptionString()
            message = _(
                "Unable to send mail: ${exception}", mapping={"exception": exception}
            )
            IStatusMessage(self.request).add(message, type="error")

    def send_feedback(self):
        IStatusMessage(self.request).add(
            _(
                "A mail has now been sent to the site administrator "
                "regarding your questions and/or comments."
            )
        )
