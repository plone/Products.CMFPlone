"""
PasswordResetTool doctests
"""

from plone.testing import layered
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

import doctest
import re
import unittest


OPTIONFLAGS = (
    doctest.ELLIPSIS
    | doctest.NORMALIZE_WHITESPACE  # |
    #               doctest.REPORT_ONLY_FIRST_FAILURE
)


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        want = re.sub("u'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    return unittest.TestSuite(
        (
            layered(
                doctest.DocFileSuite(
                    "pwreset_browser.rst",
                    optionflags=OPTIONFLAGS,
                    package="Products.CMFPlone.tests",
                    checker=Py23DocChecker(),
                ),
                layer=PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING,
            ),
        )
    )
