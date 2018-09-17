# -*- coding: utf-8 -*-
from plone.app.layout.testing import FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import unittest


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
                layer=FUNCTIONAL_TESTING)
        for test in normal_testfiles])
    return suite
