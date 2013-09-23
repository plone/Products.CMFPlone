from doctest import DocTestSuite, DocFileSuite
from plone.app.testing.bbb import PloneTestCase
from Testing.ZopeTestCase import ZopeDocTestSuite
from unittest import TestSuite


def test_suite():
    suites = (
        DocFileSuite('messages.txt', package='Products.CMFPlone.tests'),
        DocTestSuite('Products.CMFPlone.CalendarTool'),
        DocTestSuite('Products.CMFPlone.i18nl10n'),
        ZopeDocTestSuite('Products.CMFPlone.PloneTool',
                         test_class=PloneTestCase),
        DocTestSuite('Products.CMFPlone.TranslationServiceTool'),
        DocTestSuite('Products.CMFPlone.utils'),
        DocTestSuite('Products.CMFPlone.workflow'),
        )

    return TestSuite(suites)
