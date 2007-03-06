from zope.testing import doctest
from unittest import TestSuite

from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

from zope.component import getUtility
from Products.CMFCore.interfaces import IPropertiesTool

setupPloneSite()

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

class SiteMapTestCase(FunctionalTestCase):
    """base test case with convenience methods for all sitemap tests"""

    def afterSetUp(self):
        super(SiteMapTestCase, self).afterSetUp()
        from Products.Five.testbrowser import Browser
        self.browser = Browser()
        
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('root', 'secret', ['Manager'], [])
        
        self.ptool = getUtility(IPropertiesTool)
        self.site_props = self.ptool.site_properties
        
    def loginAsManager(self):
        """points the browser to the login screen and logs in as user root
        with Manager role."""

        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = 'root'
        self.browser.getControl('Password').value = 'secret'
        self.browser.getControl('Log in').click()


def test_suite():
    tests = ['sitemap.txt']
    suite = TestSuite()
    for test in tests:
        suite.addTest(FunctionalDocFileSuite(test,
            optionflags=OPTIONFLAGS,
            package="plone.app.layout.sitemap.tests",
            test_class=SiteMapTestCase))
    return suite
