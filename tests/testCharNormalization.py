#
# Tests the charNormalization method
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

default_user = PloneTestCase.default_user

from Products.CMFPlone.CharNormalization import charNormalization

class TestCharNormalization(PloneTestCase.PloneTestCase):

    def testCharNormalization(self):
        # European accented chars will be transliterated to rough ASCII equivalents
        self.assertEqual(charNormalization(self.portal, u"Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5"), 'Eksempel eoa norsk EOA')

    def testCharNormalizationChars(self):
        self.assertEqual(charNormalization(self.portal, u"\xe6"), 'e')
        self.assertEqual(charNormalization(self.portal, u"a"), 'a')
        self.assertEqual(charNormalization(self.portal, u"\u9ad8"), '9ad8')

    def testCharNormalizationUTF8(self):
        # In real life, input will not be Unicode...
        input = u"Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5".encode('utf-8')
        self.assertEqual(charNormalization(self.portal, input, 'utf-8'),
                         'Eksempel eoa norsk EOA')

    def testCharNormalizationGerman(self):
        # German normalization mapping
        input = u"\xc4ffin"
        self.assertEqual(charNormalization(self.portal, input),
                         'Aeffin')

    def testCharNormalizationUTF8Default(self):
        # In real life, input will not be Unicode...
        input = u"Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5".encode('utf-8')
        self.assertEqual(charNormalization(self.portal, input),
                         'Eksempel eoa norsk EOA')

    def testCharNormalizationWithNumbers(self):
        # Mixed numbers with text
        self.assertEqual(charNormalization(self.portal, u"Eksempel-1-2-3-\xe6\xf8\xe5 norsk \xc6\xd8\xc5"), 'Eksempel-1-2-3-eoa norsk EOA')

    def testCharNormalizationGreek(self):
        # Greek letters (not supported by UnicodeData)
        self.assertEqual(charNormalization(self.portal, u'\u039d\u03af\u03ba\u03bf\u03c2 \u03a4\u03b6\u03ac\u03bd\u03bf\u03c2'), 'Nikos Tzanos')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCharNormalization))
    return suite

if __name__ == '__main__':
    framework()
