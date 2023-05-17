# Test toLocalizedTime script and TranslationServiceTool.

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests import PloneTestCase


class TestUTranslate(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.tool = getToolByName(self.portal, "translation_service")

    def testUTranslate(self):
        # Test Unicode value
        value = self.tool.translate("foo", "domain")
        self.assertEqual(value, "foo")

        # Test ascii value
        value = self.tool.translate("foo", "domain")
        self.assertEqual(value, "foo")

        # Test empty string
        value = self.tool.translate("", "domain")
        self.assertEqual(value, "")

        # Test empty domain
        value = self.tool.translate("foo", "domain")
        self.assertEqual(value, "foo")

        # Test default is None
        value = self.tool.translate("foo", "domain", default=None)
        self.assertEqual(value, "foo")


class TestTranslationServiceTool(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.tool = getToolByName(self.portal, "translation_service")

    def testLocalized_time(self):
        value = self.tool.ulocalized_time(
            "Mar 9, 1997 1:45pm", long_format=True, time_only=False, context=self.portal
        )
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        self.assertEqual(value, "Mar 09, 1997 01:45 PM")

    def testLocalized_time_only_none(self):
        value = self.tool.ulocalized_time(
            "Mar 9, 1997 1:45pm", long_format=True, time_only=None, context=self.portal
        )
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        self.assertEqual(value, "Mar 09, 1997 01:45 PM")

    def testLocalized_time_only(self):
        value = self.tool.ulocalized_time(
            "Mar 9, 1997 1:45pm", long_format=True, time_only=True, context=self.portal
        )
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        self.assertEqual(value, "01:45 PM")

    def test_ulocalized_time_fetch_error(self):
        # http://dev.plone.org/plone/ticket/4251
        error = "(Missing.Value,), {}"
        value = self.tool.ulocalized_time(error)
        self.assertEqual(value, None)
