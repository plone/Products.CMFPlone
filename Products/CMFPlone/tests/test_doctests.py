from doctest import DocTestSuite, DocFileSuite
from Products.CMFPlone.tests.PloneTestCase import FunctionalTestCase
from Testing.ZopeTestCase import ZopeDocTestSuite
from unittest import TestSuite


def test_suite():
    suites = (
        DocFileSuite('messages.txt', package='Products.CMFPlone.tests'),
        DocTestSuite('Products.CMFPlone.i18nl10n'),
        ZopeDocTestSuite('Products.CMFPlone.PloneTool',
                         test_class=FunctionalTestCase),
        DocTestSuite('Products.CMFPlone.TranslationServiceTool'),
        DocTestSuite('Products.CMFPlone.utils'),
        DocTestSuite('Products.CMFPlone.workflow'),
        )

    return TestSuite(suites)
