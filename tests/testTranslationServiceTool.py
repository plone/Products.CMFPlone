#
# Test toLocalizedTime script and TranslationServiceTool.
#
# Tries to cover http://plone.org/products/plone/roadmap/98
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

from DateTime.DateTime import DateTime


class TestToLocalizedTime(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.script = self.portal.toLocalizedTime

    def testDateTimeArg(self):
        value = self.script(DateTime('Mar 9, 1997 1:45pm'),
                            long_format=True)
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        self.assertEquals(value, '1997-03-09 13:45')

    def testStringArg(self):
        value = self.script('Mar 9, 1997 1:45pm', long_format=True)
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        self.assertEquals(value, '1997-03-09 13:45')


class TestUTranslate(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = self.portal.translation_service

    def testUTranslate(self):
        # Test Unicode value
        value = self.tool.utranslate('domain', u'foo')
        self.assertEquals(value, u'foo')

        # Test ascii value
        value = self.tool.utranslate('domain', 'foo')
        self.assertEquals(value, u'foo')

        # Test utf-8 value
        value = self.tool.utranslate('domain', u'\xc3'.encode('utf-8'))
        self.assertEquals(value, u'\xc3')

        # Test iso8859-1 value, should be replaced
        value = self.tool.utranslate('domain', u'\xc3'.encode('iso8859-1'))
        self.assertEquals(value, u'\ufffd')

        # Test empty string
        value = self.tool.utranslate('domain', '')
        self.assertEquals(value, u'')

        # Test empty domain
        value = self.tool.utranslate('', 'foo')
        self.assertEquals(value, u'foo')

        # Test default is None
        value = self.tool.utranslate('domain', 'foo', default=None)
        self.assertEquals(value, u'foo')

class TestTranslationServiceTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.tool = self.portal.translation_service

    def testLocalized_time(self):
        value = self.tool.ulocalized_time('Mar 9, 1997 1:45pm',
                                         long_format=True)
        # TranslationServiceTool falls back to time formats in site properties
        # because PTS isn't installed
        self.assertEquals(value, '1997-03-09 13:45')

    def test_ulocalized_time_fetch_error(self):
        # http://dev.plone.org/plone/ticket/4251
        error = "(Missing.Value,), {}"
        value = self.tool.ulocalized_time(error)
        self.failUnlessEqual(value, None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestToLocalizedTime))
    suite.addTest(makeSuite(TestUTranslate))
    suite.addTest(makeSuite(TestTranslationServiceTool))
    return suite

if __name__ == '__main__':
    framework()
