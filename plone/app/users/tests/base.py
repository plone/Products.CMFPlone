"""Base class for flexible user registration test cases.

This is in a separate module because it's potentially useful to other
packages which register accountpanels. They should be able to import it
without the PloneTestCase.setupPloneSite() side effects.
"""

from Products.PloneTestCase.PloneTestCase import FunctionalTestCase

from Acquisition import aq_base
from zope.component import getSiteManager
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from Products.CMFCore.utils import getToolByName

# BBB Zope 2.12
try:
    from Testing.testbrowser import Browser
except ImportError:
    from Products.Five.testbrowser import Browser

from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.Cache import Cacheable
from Products.PluggableAuthService.interfaces.plugins import IValidationPlugin, IPropertiesPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.CMFCore.interfaces import ISiteRoot
from zope.component import getUtility, getAdapter
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces


class TestCase(FunctionalTestCase):
    """base test case which adds amin user"""


    def afterSetUp(self):
        super(TestCase, self).afterSetUp()
        self.browser = Browser()
        self.portal.acl_users._doAddUser('admin', 'secret', ['Manager'], [])

        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        self.membership = self.portal.portal_membership
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

    def addParrotPasswordPolicy(self):
        # remove default policy
        uf = self.portal.acl_users
        for policy in uf.objectIds(['Default Plone Password Policy']):
            uf.plugins.deactivatePlugin(IValidationPlugin, policy)

        obj = DeadParrotPassword('test')
        uf._setObject(obj.getId(), obj)
        obj = uf[obj.getId()]
        activatePluginInterfaces(self.portal, obj.getId())

        portal = getUtility(ISiteRoot)
        pas_instance = portal.acl_users
        plugins = pas_instance._getOb('plugins')
        validators = plugins.listPlugins(IValidationPlugin)
        assert validators

    def activateDefaultPasswordPolicy(self):
        uf = self.portal.acl_users
        plugins = uf._getOb('plugins')
        for policy in uf.objectIds(['Default Plone Password Policy']):
            activatePluginInterfaces(self.portal, policy)
            validators = plugins.listPlugins(IValidationPlugin)
            #assert policy in validators

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)

        portal = getUtility(ISiteRoot)
        pas_instance = portal.acl_users
        plugin = getattr(pas_instance,'test', None)
        if plugin is not None:
            plugins = pas_instance._getOb('plugins')
            plugins.deactivatePlugin(IValidationPlugin, 'test')
            #plugins.deactivatePlugin(IPropertiesPlugin, 'test')
            pas_instance.manage_delObjects('test')


    def setMailHost(self):
        self.portal.MailHost.smtp_host = 'localhost'
        setattr(self.portal, 'email_from_address', 'admin@foo.com')

    def unsetMailHost(self):
        self.portal.MailHost.smtp_host = ''
        setattr(self.portal, 'email_from_address', '')

# Dummy password validation PAS plugin



class DeadParrotPassword(BasePlugin, Cacheable):
    meta_type = 'Test Password Strength Plugin'
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title

    security.declarePrivate('validateUserInfo')
    def validateUserInfo(self, user, set_id, set_info ):

        errors = []

        if set_info and set_info.get('password', None) is not None:
            password = set_info['password']
            if password.count('dead') or password == '':
                errors = [{'id':'password','error':u'Must not be dead'}]
            else:
                errors = []
        return errors


classImplements(DeadParrotPassword,
                IValidationPlugin)
