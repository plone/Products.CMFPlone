# -*- coding: utf-8 -*-
from plone.testing import layered
from plone.app.layout.testing import FUNCTIONAL_TESTING

import doctest
import unittest


OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

normal_testfiles = [
    'analytics.txt',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test,
                                     optionflags=OPTIONFLAGS,
                                     ),
                layer=FUNCTIONAL_TESTING)
        for test in normal_testfiles])
    return suite
