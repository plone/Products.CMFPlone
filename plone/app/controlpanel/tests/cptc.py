"""Base class for control panel test cases.

This is in a separate module because it's potentially useful to other
packages which register controlpanels. They should be able to import it
without the PloneTestCase.setupPloneSite() side effects.
"""

from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName

class ControlPanelTestCase(FunctionalTestCase):
    """base test case with convenience methods for all control panel tests"""
    
    def afterSetUp(self):
        super(ControlPanelTestCase, self).afterSetUp()
        
        self.browser = Browser()
        
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('root', 'secret', ['Manager'], [])
        
        self.ptool = getToolByName(self.portal, 'portal_properties')
        self.site_props = self.ptool.site_properties
    
    def loginAsManager(self, user='root', pwd='secret'):
        """points the browser to the login screen and logs in as user root with Manager role."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()

