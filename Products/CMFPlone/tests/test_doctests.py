from unittest import TestSuite

import doctest


def test_suite():
    suites = (
        doctest.DocTestSuite("Products.CMFPlone.TranslationServiceTool"),
        doctest.DocTestSuite("Products.CMFPlone.utils"),
        doctest.DocTestSuite("Products.CMFPlone.workflow"),
    )

    return TestSuite(suites)
