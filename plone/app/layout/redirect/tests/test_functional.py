import urllib

from zope.testing import doctest
from unittest import TestSuite, makeSuite

from Products.Five.testbrowser import Browser

from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Products.CMFCore.utils import getToolByName

setupPloneSite()

class TestRedirect(FunctionalTestCase):

    def afterSetUp(self):
        super(TestRedirect, self).afterSetUp()
        self.browser = Browser()

    def test_relative(self):
        portal_url = self.portal.absolute_url()
        url = portal_url+'/@@plone_redirect?dest=Members'
        self.browser.open(url)
        self.assertEqual(self.browser.url, 'http://nohost/plone/Members')

    def test_absolute(self):
        portal_url = self.portal.absolute_url()
        abs_url = urllib.quote(portal_url+'/Members')
        url = portal_url+'/@@plone_redirect?dest='+abs_url
        self.browser.open(url)
        self.assertEqual(self.browser.url, 'http://nohost/plone/Members')

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestRedirect))
    return suite
