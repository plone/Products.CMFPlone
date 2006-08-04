#
# Tests the UnicodeSplitter
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.UnicodeSplitter import Splitter


class TestSplitter(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.splitter = Splitter()
        self.process = self.splitter.process
        self.processGlob = self.splitter.processGlob
                         
    def testProcessGerman(self):
        # German letters
        input = [u"\xc4ffin"]
        self.assertEqual(self.process(input), input)
        self.assertEqual(self.processGlob(input), input)

        input = ["\xc4ffin"]
        self.assertEqual(self.process(input), input)
        self.assertEqual(self.processGlob(input), input)

    def testProcessGreek(self):
        # Greek letters
        input = [u'\u039d\u03af\u03ba\u03bf\u03c2 \u03a4\u03b6\u03ac\u03bd\u03bf\u03c2']
        output = [u'\u039d\u03af\u03ba\u03bf\u03c2',
                  u'\u03a4\u03b6\u03ac\u03bd\u03bf\u03c2']

        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

        input = [t.encode('utf-8') for t in input]
        output = [t.encode('utf-8') for t in output]

        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

    def testProcessTurkish(self):
        # Turkish letters
        input = [u"\xdc\u011f\xfcr"]
        self.assertEqual(self.process(input), input)
        self.assertEqual(self.processGlob(input), input)

        input = [t.encode('utf-8') for t in input]
        self.assertEqual(self.process(input), input)
        self.assertEqual(self.processGlob(input), input)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSplitter))
    return suite

if __name__ == '__main__':
    framework()
