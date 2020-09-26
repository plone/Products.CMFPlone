from plone.app.robotframework.remote import RemoteLibrary
from plone.app.robotframework.utils import disableCSRFProtection

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IMailSchema
from Products.CMFPlone.interfaces import ISecuritySchema


class CMFPloneRemoteKeywords(RemoteLibrary):
    """Robot Framework remote keywords library
    """

    def the_mail_setup_configured(self):
        disableCSRFProtection()
        registry = queryUtility(IRegistry)
        if registry is None:
            return
        mail_settings = registry.forInterface(IMailSchema, prefix='plone')
        if mail_settings is None:
            return
        mail_settings.smtp_host = 'localhost'
        mail_settings.email_from_address = 'john@doe.com'

    def the_self_registration_enabled(self):
        disableCSRFProtection()
        registry = queryUtility(IRegistry)
        if registry is None:
            return
        security_settings = registry.forInterface(
            ISecuritySchema, prefix='plone')
        if security_settings is None:
            return
        security_settings.enable_self_reg = True
