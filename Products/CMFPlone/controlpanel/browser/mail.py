from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.MailHost.MailHost import MailHostError
from Products.statusmessages.interfaces import IStatusMessage
from logging import getLogger
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from z3c.form import button
from zope.component import getUtility

import smtplib
import socket
import sys

log = getLogger('Plone')


class MailControlPanelForm(controlpanel.RegistryEditForm):

    id = "MailControlPanel"
    label = _(u"Mail settings")
    schema = IMailSchema
    schema_prefix = "plone"

    @button.buttonAndHandler(_('Save'), name=None)
    def handleSave(self, action):
        super(MailControlPanelForm, self).handleSave(self, action)

    @button.buttonAndHandler(_('Cancel'), name='cancel')
    def handleCancel(self, action):
        super(MailControlPanelForm, self).handleCancel(self, action)

    @button.buttonAndHandler(
        _('label_smtp_test', default='Save and send test e-mail'),
        name='test')
    def handle_test_action(self, action):
        data = self.request.form
        # Save data first
        self.handle_edit_action.success(data)
        mailhost = getToolByName(self.context, 'MailHost')

        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        fromaddr = mail_settings.email_from_address
        fromname = self.mail_settings.email_from_name

        message = ("Hi,\n\nThis is a test message sent from the Plone "
                   "'Mail settings' control panel. Your receipt of this "
                   "message (at the address specified in the Site 'From' "
                   "address field) indicates that your e-mail server is "
                   "working!\n\n"
                   "Have a nice day.\n\n"
                   "Love,\n\nPlone")
        email_charset = mail_settings.email_charset
        email_recipient, source = fromaddr, fromaddr
        subject = "Test e-mail from Plone"

        # Make the timeout incredibly short. This is enough time for most mail
        # servers, wherever they may be in the world, to respond to the
        # connection request. Make sure we save the current value
        # and restore it afterward.
        timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(3)
            try:
                mailhost.send(message, email_recipient, source,
                              mfrom=fromname,
                              subject=subject,
                              charset=email_charset,
                              immediate=True)

            except (socket.error, MailHostError, smtplib.SMTPException):
                # Connection refused or timeout.
                log.exception('Unable to send test e-mail.')
                value = sys.exc_info()[1]
                msg = _(u'Unable to send test e-mail ${error}.',
                        mapping={'error': unicode(value)})
                IStatusMessage(self.request).addStatusMessage(
                    msg, type='error')
            else:
                IStatusMessage(self.request).addStatusMessage(
                    _(u'Success! Check your mailbox for the test message.'),
                    type='info')
        finally:
            # Restore timeout to default value
            socket.setdefaulttimeout(timeout)


class MailControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MailControlPanelForm
