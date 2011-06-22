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

    def addPasswordStrength(self):
        obj = TestPasswordStrength('test')
        self.portal.acl_users._setObject(obj.getId(), obj)
        obj = self.portal.acl_users[obj.getId()]
        obj.manage_activateInterfaces(['IValidationPlugin','IPropertiesPlugin'])

        portal = getUtility(ISiteRoot)
        pas_instance = portal.acl_users
        plugins = pas_instance._getOb('plugins')
        validators = plugins.listPlugins(IValidationPlugin)
        assert validators


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



class TestPasswordStrength(BasePlugin, Cacheable):
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

    def getPropertiesForUser(self, user):
        return {'generated_password':'alive parrot'}


classImplements(TestPasswordStrength,
                IValidationPlugin)
classImplements(TestPasswordStrength,
                IPropertiesPlugin)
