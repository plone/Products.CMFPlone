"""Base class for integration tests, based on ZopeTestCase and PloneTestCase.

Note that importing this module has various side-effects: it registers a set of
products with Zope, and it sets up a sandbox Plone site with the appropriate
products installed.
"""

from Testing import ZopeTestCase

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# Set up a Plone site - note that the portlets branch of CMFPlone applies
# a portlets profile.
setupPloneSite()

class PortletsTestCase(PloneTestCase):
    """Base class for integration tests for plone.app.portlets. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """

class PortletsFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for plone.app.portlets. 
    This may provide specific set-up and tear-down operations, or provide 
    convenience methods.
    """