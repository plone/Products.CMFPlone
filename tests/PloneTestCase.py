#
# PloneTestCase
#

# $Id$

from plone.app.blob import db   # needs to be imported first to set up ZODB
from Products.PloneTestCase.ptc import *

# Make the test fixture extension profile active
from zope.interface import classImplements
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.interfaces import ITestCasePloneSiteRoot

classImplements(PloneSite, ITestCasePloneSiteRoot)

from plone.app.blob.tests import setupPackage
setupPackage()

setupPloneSite(extension_profiles=['Products.CMFPlone:testfixture', 'plone.app.blob:testing'])


class PloneTestCase(PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """

    def setRequestMethod(self, method):
        self.app.REQUEST.set('REQUEST_METHOD', method)
        self.app.REQUEST.method = method


class FunctionalTestCase(Functional, PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """
