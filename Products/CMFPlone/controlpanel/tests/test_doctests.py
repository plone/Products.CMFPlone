from plone.testing import layered
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

import doctest
import re
import unittest


tests = ("../README.rst",)


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        # TODO: Fix tests to use Python 3 syntax
        want = re.sub("u'(.*?)'", "'\\1'", want)
        want = re.sub('u"(.*?)"', '"\\1"', want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    return unittest.TestSuite(
        [
            layered(
                doctest.DocFileSuite(
                    ft,
                    optionflags=doctest.ELLIPSIS,
                    checker=Py23DocChecker(),
                ),
                layer=PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING,
            )
            for ft in tests
        ]
    )
