# -*- coding: utf-8 -*-
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from plone.testing import layered
import doctest
import unittest


tests = ('../README.rst',)


def test_suite():
    return unittest.TestSuite(
        [
            layered(
                doctest.DocFileSuite(f, optionflags=doctest.ELLIPSIS),
                layer=PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
            )
            for f in tests
        ]
    )
