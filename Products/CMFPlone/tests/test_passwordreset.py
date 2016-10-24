"""
PasswordResetTool doctests
"""

import doctest
import unittest

from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from plone.testing import layered


OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE # |
#               doctest.REPORT_ONLY_FIRST_FAILURE
               )


def test_suite():
    return unittest.TestSuite((
        layered(
            doctest.DocFileSuite(
                'pwreset_browser.txt',
                optionflags=OPTIONFLAGS,
                package='Products.CMFPlone.tests',
            ),
            layer=PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
        ),
    ))
