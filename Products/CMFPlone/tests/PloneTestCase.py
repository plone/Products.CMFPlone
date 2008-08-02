#
# PloneTestCase
#

# $Id$

from Products.PloneTestCase.ptc import *

# Make the test fixture extension profile active
from zope.interface import classImplements
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.interfaces import ITestCasePloneSiteRoot
classImplements(PloneSite, ITestCasePloneSiteRoot)

setupPloneSite(extension_profiles=['Products.CMFPlone:testfixture'])

from plone.protect.authenticator import AuthenticatorView
from re import match


class PloneTestCase(PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

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
