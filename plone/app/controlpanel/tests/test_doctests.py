from zope.testing import doctest
from unittest import TestSuite

from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

setupPloneSite()

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    suites = (
        FunctionalDocFileSuite('calendar.txt',
            optionflags=OPTIONFLAGS,
            package='Products.CMFPlone.browser.controlpanel.tests',
            test_class=FunctionalTestCase),
        FunctionalDocFileSuite('mail.txt',
            optionflags=OPTIONFLAGS,
            package='Products.CMFPlone.browser.controlpanel.tests',
            test_class=FunctionalTestCase),
        FunctionalDocFileSuite('search.txt',
            optionflags=OPTIONFLAGS,
            package='Products.CMFPlone.browser.controlpanel.tests',
            test_class=FunctionalTestCase),
        )

    return TestSuite(suites)
