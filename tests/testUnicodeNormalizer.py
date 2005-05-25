#
# Tests the normalizeUnicode method
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.UnicodeNormalizer import normalizeUnicode


class TestNormalizer(PloneTestCase.PloneTestCase):

    def testNormalize(self):
        # European accented chars will be transliterated to rough ASCII equivalents
        input = u"Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5"
        self.assertEqual(normalizeUnicode(input),
                         'Eksempel eoa norsk EOA')

    def testNormalizeSingleChars(self):
        self.assertEqual(normalizeUnicode(u"\xe6"), 'e')
        self.assertEqual(normalizeUnicode(u"a"), 'a')
        self.assertEqual(normalizeUnicode(u"\u9ad8"), '9ad8')

    def testNormalizeGerman(self):
        # German normalization mapping
        input = u"\xc4ffin"
        self.assertEqual(normalizeUnicode(input), 'Aeffin')

    def testNormalizeWithNumbers(self):
        # Mixed numbers with text
        input = u"Eksempel-1-2-3-\xe6\xf8\xe5 norsk \xc6\xd8\xc5"
        self.assertEqual(normalizeUnicode(input),
                         'Eksempel-1-2-3-eoa norsk EOA')

    def testNormalizeGreek(self):
        # Greek letters (not supported by UnicodeData)
        input = u'\u039d\u03af\u03ba\u03bf\u03c2 \u03a4\u03b6\u03ac\u03bd\u03bf\u03c2'
        self.assertEqual(normalizeUnicode(input), 'Nikos Tzanos')

    def testNormalizeNonUnicode(self):
        # Non-unicode input raises a TypeError
        self.assertRaises(TypeError, normalizeUnicode, 'foo')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestNormalizer))
    return suite

if __name__ == '__main__':
    framework()
