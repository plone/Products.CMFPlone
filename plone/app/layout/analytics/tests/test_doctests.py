import unittest
import doctest
from Testing import ZopeTestCase as ztc

from plone.app.layout.analytics.tests import base

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return unittest.TestSuite((
        ztc.ZopeDocFileSuite(
            'tests/analytics.txt', package='plone.app.layout.analytics',
            test_class=base.AnalyticsFunctionalTestCase,
            optionflags=OPTIONFLAGS),
    ))
