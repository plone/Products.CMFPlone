# -*- coding: utf-8 -*-
from plone.app.layout.analytics.tests import base
from Testing import ZopeTestCase as ztc

import doctest
import unittest


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
