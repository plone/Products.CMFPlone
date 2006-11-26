from zope.testing import doctest
from unittest import TestSuite

from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.CMFPlone.tests import PloneTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def test_suite():
    suites = (
        FunctionalDocFileSuite('calendar.txt',
            optionflags=OPTIONFLAGS,
            package='Products.CMFPlone.browser.controlpanel.tests',
            test_class=PloneTestCase.FunctionalTestCase),
        FunctionalDocFileSuite('mail.txt',
            optionflags=OPTIONFLAGS,
            package='Products.CMFPlone.browser.controlpanel.tests',
            test_class=PloneTestCase.FunctionalTestCase),
        FunctionalDocFileSuite('search.txt',
            optionflags=OPTIONFLAGS,
            package='Products.CMFPlone.browser.controlpanel.tests',
            test_class=PloneTestCase.FunctionalTestCase),
        )

    return TestSuite(suites)
