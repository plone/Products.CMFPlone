#
# PloneTestCase
#

#from Products.PloneTestCase.ptc import *
from Products.PloneTestCase.ptc import Functional
from Products.PloneTestCase.ptc import PloneTestCase as ptc
from Products.PloneTestCase.ptc import default_password
from Products.PloneTestCase.ptc import default_user
from Products.PloneTestCase.ptc import setupPloneSite
from Testing.testbrowser import Browser

# used by other modules
from Products.PloneTestCase.ptc import portal_name
from Products.PloneTestCase.ptc import installProduct
from Products.PloneTestCase.ptc import portal_owner

# Make the test fixture extension profile active
from zope.interface import classImplements
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.interfaces import ITestCasePloneSiteRoot
classImplements(PloneSite, ITestCasePloneSiteRoot)

TEST_PROFILE = 'Products.CMFPlone:testfixture'

from plone.protect.authenticator import AuthenticatorView
from re import match

try:
    # plone.app.event integration
    from plone.app.event.testing import set_timezone
except:
    set_timezone = None


setupPloneSite(extension_profiles=[TEST_PROFILE])


class PloneTestCase(ptc):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

    def _setup(self):
        super(PloneTestCase, self)._setup()
        if set_timezone:
            set_timezone('UTC')

    def setRequestMethod(self, method):
        self.app.REQUEST.set('REQUEST_METHOD', method)
        self.app.REQUEST.method = method

    def getAuthenticator(self):
        tag = AuthenticatorView('context', 'request').authenticator()
        pattern = '<input .*name="(\w+)".*value="(\w+)"'
        return match(pattern, tag).groups()

    def setupAuthenticator(self):
        name, token = self.getAuthenticator()
        self.app.REQUEST.form[name] = token


class FunctionalTestCase(Functional, PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            user = default_user
            pwd = default_password
            browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
        return browser
