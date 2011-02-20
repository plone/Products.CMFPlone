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
        obj.manage_activateInterfaces(['IValidationPlugin'])


    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost), provided=IMailHost)

        try:
            self.portal.acl_users.manage_delObjects('test')
        except:
            pass


    def setMailHost(self):
        self.portal.MailHost.smtp_host = 'localhost'
        setattr(self.portal, 'email_from_address', 'admin@foo.com')

    def unsetMailHost(self):
        self.portal.MailHost.smtp_host = ''
        setattr(self.portal, 'email_from_address', '')

# Dummy password validation PAS plugin

from AccessControl.SecurityInfo import ClassSecurityInfo
from OFS.Cache import Cacheable
from Products.PluggableAuthService.interfaces.plugins import IValidationPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements


class TestPasswordStrength(BasePlugin, Cacheable):
    meta_type = 'Test Password Strength Plugin'
    security = ClassSecurityInfo()

    def __init__(self, id, title=None):
        self._id = self.id = id
        self.title = title

    security.declarePrivate('validateUserInfo')
    def validateUserInfo(self, user, set_id, set_info ):

        errors = []

        if set_info and set_info.get('password', None):
            password = set_info['password']

            errors = [{'id':'password','error':u'Must be not be dead'}]
        return errors


classImplements(TestPasswordStrength,
                IValidationPlugin)
