from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.utils import safe_hasattr
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.interface import implements
from zope.site.hooks import getSite


class MailControlPanelAdapter(object):

    adapts(IPloneSiteRoot)
    implements(IMailSchema)

    def __init__(self, context):
        self.context = context
        self.portal = getSite()
        registry = getUtility(IRegistry)
        self.encoding = 'utf-8'
        self.mail_settings = registry.forInterface(
            IMailSchema, prefix="plone")

    def get_smtp_host(self):
        return self.mail_settings.smtp_host

    def set_smtp_host(self, value):
        if safe_hasattr(self.mail_settings, 'smtp_host'):
            self.mail_settings.smtp_host = value

    smtp_host = property(get_smtp_host, set_smtp_host)

    def get_smtp_port(self):
        return getattr(self.mail_settings, 'smtp_port', None)

    def set_smtp_port(self, value):
        if safe_hasattr(self.mail_settings, 'smtp_port'):
            self.mail_settings.smtp_port = value

    smtp_port = property(get_smtp_port, set_smtp_port)

    def get_smtp_userid(self):
        return getattr(self.mail_settings, 'smtp_userid',
                       getattr(self.mail_settings, 'smtp_userid', None))

    def set_smtp_userid(self, value):
        if safe_hasattr(self.mail_settings, 'smtp_userid'):
            self.mail_settings.smtp_userid = value
            #SecureMailhost 1.x also uses this:
            if safe_hasattr(self.mail_settings, '_smtp_userid'):
                self.mail_settings._smtp_userid = value
        elif safe_hasattr(self.mail_settings, 'smtp_userid'):
            self.mail_settings.smtp_uid = value

    smtp_userid = property(get_smtp_userid, set_smtp_userid)

    def get_smtp_pass(self):
        return getattr(self.mail_settings, 'smtp_pass',
                       getattr(self.mail_settings, 'smtp_pwd', None))

    def set_smtp_pass(self, value):
        # Don't update the value, if we don't get a new one
        if value is not None:
            if safe_hasattr(self.mail_settings, 'smtp_pass'):
                self.mail_settings.smtp_pass = value
                #SecureMailhost 1.x also uses this:
                if safe_hasattr(self.mail_settings, '_smtp_pass'):
                    self.mail_settings._smtp_pass = value
            elif safe_hasattr(self.mail_settings, 'smtp_pwd'):
                self.mail_settings.smtp_pwd = value

    smtp_pass = property(get_smtp_pass, set_smtp_pass)

    def get_email_from_name(self):
        return self.mail_settings.email_from_name

    def set_email_from_name(self, value):
        self.mail_settings.email_from_name = value

    email_from_name = property(get_email_from_name, set_email_from_name)

    def get_email_from_address(self):
        return self.mail_settings.email_from_address

    def set_email_from_address(self, value):
        self.mail_settings.email_from_address = value

    email_from_address = property(get_email_from_address,
                                  set_email_from_address)
