"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

#from Testing import ZopeTestCase
#import doctest
#from unittest import TestSuite

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase import PloneTestCase
from plone.app.portlets.tests import layer

# BBB Zope 2.12
try:
    from Testing.testbrowser import Browser
    Browser # pyflakes
except ImportError:
    from Products.Five.testbrowser import Browser

# Set up a Plone site - note that the portlets branch of CMFPlone applies
# a portlets profile.
PloneTestCase.setupPloneSite()


class PortletsTestCase(PloneTestCase.PloneTestCase):
    """Base class for integration tests for plone.app.portlets. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """


class PortletsFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """Base class for functional integration tests for plone.app.portlets.
    This may provide specific set-up and tear-down operations, or provide
    convenience methods.
    """

    layer = layer.PlonePortlets

    def afterSetUp(self):
        """ set up the tests """
        pass

    def getBrowser(self, loggedIn=False, admin=False):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            u = PloneTestCase.default_user
            p = PloneTestCase.default_password
            browser.open(self.portal.absolute_url() + "/login_form")
            browser.getControl(name='__ac_name').value = u
            browser.getControl(name='__ac_password').value = p
            browser.getControl(name='submit').click()
        return browser
