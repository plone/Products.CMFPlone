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
        self.membership = self.portal.portal_membership

    def loginAsMember(self, user='test_user_1_', pwd='secret'):
        """points the browser to the login screen and logs in as user 'user'."""
        self.browser.open('http://nohost/plone/')
        self.browser.getLink('Log in').click()
        self.browser.getControl('Login Name').value = user
        self.browser.getControl('Password').value = pwd
        self.browser.getControl('Log in').click()

