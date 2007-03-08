from plone.fieldsets import FormFieldsets

from zope.interface import Interface
from zope.component import adapts
from zope.component import getUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Int
from zope.schema import Password
from zope.schema import TextLine

from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr
from Products.MailHost.interfaces import IMailHost

from form import ControlPanelForm

class IMailHostSchema(Interface):

    smtp_host = TextLine(title=_(u'SMTP server'),
                         description=_(u'''The address of your local SMTP
                                       (outgoing e-mail) server. Usually
                                       "localhost", unless you use an external
                                       server to send e-mail.'''),
                         default=u'localhost',
                         required=True)

    smtp_port = Int(title=_(u'SMTP port'),
                    description=_(u'''The port of your local SMTP (outgoing
                                      e-mail) server. Usually "25".'''),
                    default=25,
                    required=True)

    smtp_userid = TextLine(title=_(u'ESMTP username'),
                           description=_(u'''Username for authentication to your
                                         e-mail server. Not required unless you
                                         are using ESMTP.'''),
                           default=None,
                           required=False)

    smtp_pass = Password(title=_(u'ESMTP password'),
                         description=_(u'The password for the ESMTP user account.'),
                         default=None,
                         required=False)


class IMailFromSchema(Interface):

    email_from_name = TextLine(title=_(u"Site 'From' name"),
                               description=_(u'''Plone generates e-mail using
                                             this name as the e-mail sender.'''),
                               default=None,
                               required=True)

    email_from_address = TextLine(title=_(u"Site 'From' address"),
                                  description=_(u'''Plone generates e-mail using
                                                this address as the e-mail
                                                return address. It is also used
                                                as the destination address on
                                                the site-wide contact form.'''),
                                  default=None,
                                  required=True)


class IMailSchema(IMailHostSchema, IMailFromSchema):
    """Combined schema for the adapter lookup.
    """


class MailControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(IMailSchema)

    def __init__(self, context):
        super(MailControlPanelAdapter, self).__init__(context)
        self.context = getUtility(IMailHost)
        pprop = getUtility(IPropertiesTool)
        self.site_properties = pprop.site_properties

    smtp_host = ProxyFieldProperty(IMailSchema['smtp_host'])
    smtp_port = ProxyFieldProperty(IMailSchema['smtp_port'])

    def get_smtp_userid(self):
        return getattr(self.context, 'smtp_userid',
                       getattr(self.context, 'smtp_uid', None))

    def set_smtp_userid(self, value):
        if safe_hasattr(self.context, 'smtp_userid'):
            self.context.smtp_userid = value
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
            elif safe_hasattr(self.context, 'smtp_pwd'):
                self.context.smtp_pwd = value

    smtp_pass = property(get_smtp_pass, set_smtp_pass)

    def get_email_from_name(self):
        return self.site_properties.email_from_name

    def set_email_from_name(self, value):
        self.site_properties.email_from_name = value

    email_from_name = property(get_email_from_name, set_email_from_name)

    def get_email_from_address(self):
        return self.site_properties.email_from_address

    def set_email_from_address(self, value):
        self.site_properties.email_from_address = value

    email_from_address = property(get_email_from_address, set_email_from_address)


mailhostset = FormFieldsets(IMailHostSchema)
mailhostset.id = 'mailhost'
mailhostset.label = _(u'Mail server')

mailfromset = FormFieldsets(IMailFromSchema)
mailfromset.id = 'mailfrom'
mailfromset.label = _(u'Mail sender')


class MailControlPanel(ControlPanelForm):

    form_fields = FormFieldsets(mailhostset, mailfromset)

    label = _("Mail settings")
    description = _("Mail settings for this Site.")
    form_name = _("Outgoing Mail Details")
