# -*- coding: utf-8 -*-
from doctest import DocTestSuite, DocFileSuite
from unittest import TestSuite


def test_suite():
    suites = (
        DocFileSuite('messages.txt', package='Products.CMFPlone.tests'),
        DocTestSuite('Products.CMFPlone.i18nl10n'),
        DocTestSuite('Products.CMFPlone.TranslationServiceTool'),
        DocTestSuite('Products.CMFPlone.utils'),
        DocTestSuite('Products.CMFPlone.workflow'),
    )

    return TestSuite(suites)
