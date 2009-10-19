"""Base class for flexible user registration test cases.

This is in a separate module because it's potentially useful to other
packages which register accountpanels. They should be able to import it
without the PloneTestCase.setupPloneSite() side effects.
"""

from zope.component import getMultiAdapter
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.Five.testbrowser import Browser
from Products.CMFCore.utils import getToolByName

class TestCase(FunctionalTestCase):
    """base test case which adds amin user"""

    def afterSetUp(self):
        super(TestCase, self).afterSetUp()
        self.browser = Browser()
        self.portal.acl_users._doAddUser('admin', 'secret', ['Manager'], [])
