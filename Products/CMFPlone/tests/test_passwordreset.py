"""
PasswordResetTool doctests
"""

import doctest
import unittest

from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FIXTURE
from plone.app import testing
from plone.registry.interfaces import IRegistry
from plone.testing import layered
from zope.component import getUtility

from Products.CMFPlone.interfaces.controlpanel import IMailSchema, ISiteSchema



OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


class Layer(testing.FunctionalTesting):

    def set_email_from_name(self, name):
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mail_settings.email_from_name = name


    def set_email_from_address(self, address):
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(IMailSchema, prefix="plone")
        mail_settings.email_from_address = address


    def set_portal_title(self, name):
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix='plone')
        site_settings.site_title = name


MM_FUNCTIONAL_TESTING = Layer(
    bases=(PRODUCTS_CMFPLONE_FIXTURE, ),
    name='PloneTestCase:Functional'
)


def test_suite():
    return unittest.TestSuite((
        layered(
            doctest.DocFileSuite(
                'pwreset_browser.txt',
                optionflags=OPTIONFLAGS,
                package='Products.CMFPlone.tests',
            ),
            layer=MM_FUNCTIONAL_TESTING
        ),
    ))
