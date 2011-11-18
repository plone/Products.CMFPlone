from logging import getLogger
import smtplib
import socket
import sys

from zope.interface import Interface
from zope.component import adapts
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.schema import Int
from zope.schema import Password
from zope.schema import TextLine
from zope.schema import ASCII
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser.textwidgets import ASCIIWidget
from zope.app.form.browser.textwidgets import PasswordWidget
from zope.app.form.browser.textwidgets import TextWidget

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr
from Products.MailHost.MailHost import MailHostError
from Products.statusmessages.interfaces import IStatusMessage

from form import ControlPanelForm

log = getLogger('Plone')

class IMailSchema(Interface):
    """Combined schema for the adapter lookup.
    """

    smtp_host = TextLine(title=_(u'label_smtp_server',
                                 default=u'SMTP server'),
                         description=_(u"help_smtp_server",
                                       default=u"The address of your local "
                                       "SMTP (outgoing e-mail) server. Usually "
                                       "'localhost', unless you use an "
                                       "external server to send e-mail."),
                         default=u'localhost',
                         required=True)

    smtp_port = Int(title=_(u'label_smtp_port',
                            default=u'SMTP port'),
                    description=_(u"help_smtp_port",
                                  default=u"The port of your local SMTP "
                                  "(outgoing e-mail) server. Usually '25'."),
                    default=25,
                    required=True)

    smtp_userid = TextLine(title=_(u'label_smtp_userid',
                                   default=u'ESMTP username'),
                           description=_(u"help_smtp_userid",
                                         default=u"Username for authentication "
                                         "to your e-mail server. Not required "
                                         "unless you are using ESMTP."),
                           default=None,
                           required=False)

    smtp_pass = Password(title=_(u'label_smtp_pass',
                                 default=u'ESMTP password'),
                         description=_(u"help_smtp_pass",
                                       default=u"The password for the ESMTP "
                                       "user account."),
                         default=None,
                         required=False)

    email_from_name = TextLine(title=_(u"Site 'From' name"),
                               description=_(u"Plone generates e-mail using "
                                              "this name as the e-mail "
                                              "sender."),
                               default=None,
                               required=True)

    email_from_address = ASCII(title=_(u"Site 'From' address"),
                               description=_(u"Plone generates e-mail using "
                                              "this address as the e-mail "
                                              "return address. It is also "
                                              "used as the destination "
                                              "address for the site-wide "
                                              "contact form and the 'Send test "
                                              "e-mail' feature."),
                               default=None,
                               required=True)


class MailControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMailSchema)

    def __init__(self, context):
        super(MailControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'MailHost')

    smtp_host = ProxyFieldProperty(IMailSchema['smtp_host'])
    smtp_port = ProxyFieldProperty(IMailSchema['smtp_port'])

    def get_smtp_userid(self):
        return getattr(self.context, 'smtp_userid',
                       getattr(self.context, 'smtp_uid', None))

    def set_smtp_userid(self, value):
        if safe_hasattr(self.context, 'smtp_userid'):
            self.context.smtp_userid = value
            #SecureMailhost 1.x also uses this:
            if safe_hasattr(self.context, '_smtp_userid'):
                self.context._smtp_userid = value
        elif safe_hasattr(self.context, 'smtp_uid'):
            self.context.smtp_uid = value

    smtp_userid = property(get_smtp_userid, set_smtp_userid)

    def get_smtp_pass(self):
        return getattr(self.context, 'smtp_pass',
                       getattr(self.context, 'smtp_pwd', None))

    def set_smtp_pass(self, value):
        # Don't update the value, if we don't get a new one
        if value is not None:
            if safe_hasattr(self.context, 'smtp_pass'):
                self.context.smtp_pass = value
                #SecureMailhost 1.x also uses this:
                if safe_hasattr(self.context, '_smtp_pass'):
                    self.context._smtp_pass = value
            elif safe_hasattr(self.context, 'smtp_pwd'):
                self.context.smtp_pwd = value

    smtp_pass = property(get_smtp_pass, set_smtp_pass)

    def get_email_from_name(self):
        return getUtility(ISiteRoot).email_from_name

    def set_email_from_name(self, value):
        getUtility(ISiteRoot).email_from_name = value

    email_from_name = property(get_email_from_name, set_email_from_name)

    def get_email_from_address(self):
        return getUtility(ISiteRoot).email_from_address

    def set_email_from_address(self, value):
        getUtility(ISiteRoot).email_from_address = value

    email_from_address = property(get_email_from_address,
                                  set_email_from_address)


class MailControlPanel(ControlPanelForm):

    form_fields = form.FormFields(IMailSchema)
    form_fields['email_from_address'].custom_widget = ASCIIWidget
    userid_widget = CustomWidgetFactory(TextWidget, extra='autocomplete="off"')
    form_fields['smtp_userid'].custom_widget = userid_widget
    pass_widget = CustomWidgetFactory(PasswordWidget, extra='autocomplete="off"')
    form_fields['smtp_pass'].custom_widget = pass_widget
    label = _("Mail settings")
    description = _("Mail settings for this site.")
    form_name = _("Mail settings")

    actions = ControlPanelForm.actions.copy()

    # 'Send test e-mail' form button
    @form.action(_(u'label_smtp_test', default=u'Save and send test e-mail'), name=u'test')
    def handle_test_action(self, action, data):
        # Save data first
        self.handle_edit_action.success(data)
        mailhost = getToolByName(self.context, 'MailHost')

        # XXX Will self.context always be the Plone site?
        fromaddr = self.context.getProperty('email_from_address')
        fromname = self.context.getProperty('email_from_name')

        message = ("Hi,\n\nThis is a test message sent from the Plone 'Mail settings' control panel. "
                   "Your receipt of this message (at the address specified in the "
                   "Site 'From' address field) "
                   "indicates that your e-mail server is working!\n\n"
                   "Have a nice day.\n\n"
                   "Love,\n\nPlone")
        email_charset = self.context.getProperty('email_charset')
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
                              subject=subject,
                              charset=email_charset,
                              immediate=True)

            except (socket.error, MailHostError, smtplib.SMTPException):
                # Connection refused or timeout.
                log.exception('Unable to send test e-mail.')
                value = sys.exc_info()[1]
                msg = _(u'Unable to send test e-mail ${error}.', mapping={'error': unicode(value)})
                IStatusMessage(self.request).addStatusMessage(msg, type='error')
            else:
                IStatusMessage(self.request).addStatusMessage(
                    _(u'Success! Check your mailbox for the test message.'),
                    type='info')
        finally:
            # Restore timeout to default value
            socket.setdefaulttimeout(timeout)
