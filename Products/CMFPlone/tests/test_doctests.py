from doctest import DocTestSuite, DocFileSuite
from unittest import TestSuite

from Products.CMFPlone.tests import PloneTestCase
from Testing.ZopeTestCase import ZopeDocTestSuite


def test_suite():
    suites = (
        DocFileSuite('messages.txt', package='Products.CMFPlone.tests'),
        DocTestSuite('Products.CMFPlone.CalendarTool'),
        ZopeDocTestSuite('Products.CMFPlone.CatalogTool',
                         test_class=PloneTestCase.FunctionalTestCase),
        DocTestSuite('Products.CMFPlone.i18nl10n'),
        ZopeDocTestSuite('Products.CMFPlone.PloneTool',
                         test_class=PloneTestCase.FunctionalTestCase),
        DocTestSuite('Products.CMFPlone.TranslationServiceTool'),
        DocTestSuite('Products.CMFPlone.utils'),
        DocTestSuite('Products.CMFPlone.workflow'),
        )

    return TestSuite(suites)
