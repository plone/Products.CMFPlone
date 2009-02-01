"""Base class for account panel test cases.

This is in a separate module because it's potentially useful to other
packages which register accountpanels. They should be able to import it
without the PloneTestCase.setupPloneSite() side effects.
"""

from zope.component import getMultiAdapter
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName

class AccountPanelTestCase(FunctionalTestCase):
    """base test case with convenience methods for all account panel tests"""

    def afterSetUp(self):
        super(AccountPanelTestCase, self).afterSetUp()
                
        self.browser = Browser()
        
        self.uf = self.portal.acl_users
        self.uf.userFolderAddUser('user1', 'secret', [], [])
        
        mt = getToolByName(self.portal, 'portal_membership')
        self.member = mt.getMemberById('user1')

        self.uf = self.portal.acl_users
        self.portal_state = self.portal.restrictedTraverse('@@plone_portal_state')

    def loginAsMember(self, user='user1', pwd='secret'):
        """points the browser to the login screen and logs in as user."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()
