# -*- coding: utf-8 -*-
"""Functional Doctests for plone.app.discussion.

   These test are only triggered when Plone 4 (and plone.testing) is installed.
"""
import doctest

import unittest2 as unittest

from plone.testing import layered
from plone.app import testing

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
normal_testfiles = [
    'history.txt',
]


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(test,
                                     optionflags=optionflags,
                                     ),
                layer=testing.PLONE_FUNCTIONAL_TESTING)
        for test in normal_testfiles])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
