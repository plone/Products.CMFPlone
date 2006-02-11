#
# Tests the normalizeUnicode method
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
PloneTestCase.setupPloneSite()

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

    def testNormalizeRussion(self):
        # Russian letters (not supported by UnicodeData)
        input = u'\u041f\u043e\u043b\u0438\u0442\u0438\u043a\u0430'
        self.assertEqual(normalizeUnicode(input), 'Politika')
        input = u'\u042d\u043a\u043e\u043d\u043e\u043c\u0438\u043a\u0430'
        self.assertEqual(normalizeUnicode(input), 'Ekonomika')
        input = u'\u041f\u041e\u0421\u041b\u0415\u0414\u041d\u0418\u0415 \u041d\u041e\u0412\u041e\u0421\u0422\u0418'
        self.assertEqual(normalizeUnicode(input), 'POSLEDNIE NOVOSTI')

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
