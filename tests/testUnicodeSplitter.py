#
# Tests the UnicodeSplitter
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from Products.CMFPlone.UnicodeSplitter import Splitter
from Products.CMFPlone.UnicodeSplitter import CaseNormalizer

import locale
LATIN1 = ('de_DE.ISO8859-15', 'de_DE.ISO8859-15@euro', 'nl_NL.iso8859-1')

def _setlocale(*names):
    saved = locale.setlocale(locale.LC_ALL)
    for name in names:
        try:
            locale.setlocale(locale.LC_ALL, name)
            break
        except locale.Error:
            pass
    else:
        return None
    return saved


class TestSplitter(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.splitter = Splitter()
        self.process = self.splitter.process
        self.processGlob = self.splitter.processGlob

    def testProcessGerman(self):
        # German letters
        input = [u"\xc4ffin foo"]
        output = [u"\xc4ffin", u"foo"]
        output = [t.encode('utf-8') for t in output]

        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

        input = [t.encode('utf-8') for t in input]
        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

    def testProcessGreek(self):
        # Greek letters
        input = [u'\u039d\u03af\u03ba\u03bf\u03c2 \u03a4\u03b6\u03ac\u03bd\u03bf\u03c2 foo']
        output = [u'\u039d\u03af\u03ba\u03bf\u03c2',
                  u'\u03a4\u03b6\u03ac\u03bd\u03bf\u03c2', u'foo']
        output = [t.encode('utf-8') for t in output]

        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

        input = [t.encode('utf-8') for t in input]
        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

    def testProcessTurkish(self):
        # Turkish letters
        input = [u"\xdc\u011f\xfcr foo"]
        output = [u"\xdc\u011f\xfcr", u"foo"]
        output = [t.encode('utf-8') for t in output]

        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

        input = [t.encode('utf-8') for t in input]
        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

    def testProcessLatin1(self):
        #
        # Test passes because plone_lexicon pipeline elements
        # are coded defensively.
        #
        input = ["\xc4ffin foo"]
        output = ["\xc4ffin", "foo"]

        # May still fail if none of the locales is available
        saved = _setlocale(*LATIN1)
        try:
            self.assertEqual(self.process(input), output)
            self.assertEqual(self.processGlob(input), output)
        finally:
            _setlocale(saved)


class TestCaseNormalizer(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.normalizer = CaseNormalizer()
        self.process = self.normalizer.process

    def testNormalizeGerman(self):
        input = [u"\xc4ffin"]
        output = [u"\xe4ffin"]
        output = [t.encode('utf-8') for t in output]

        self.assertEqual(self.process(input), output)

        input = [t.encode('utf-8') for t in input]
        self.assertEqual(self.process(input), output)

    def testNormalizeLatin1(self):
        #
        # Test passes because plone_lexicon pipeline elements
        # are coded defensively.
        #
        input = ["\xc4ffin"]
        output = ["\xe4ffin"]

        # May still fail if none of the locales is available
        saved = _setlocale(*LATIN1)
        try:
            self.assertEqual(self.process(input), output)
        finally:
            _setlocale(saved)


class TestQuery(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder._setObject('doc1', dummy.Item('doc1'))
        self.doc1 = self.folder.doc1
        self.folder._setObject('doc2', dummy.Item('doc2'))
        self.doc2 = self.folder.doc2

    def testQueryByUmlaut(self):
        self.doc1.SearchableText = '\303\204ffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='\303\204ffin')
        self.assertEqual(len(brains), 1)

    def testQueryByUmlautLower(self):
        self.doc1.SearchableText = '\303\204ffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='\303\244ffin')
        self.assertEqual(len(brains), 1)

    def testQueryDifferentiatesUmlauts(self):
        self.doc1.SearchableText = '\303\204ffin'
        self.catalog.indexObject(self.doc1)
        self.doc2.SearchableText = '\303\226ffin'
        self.catalog.indexObject(self.doc2)
        brains = self.catalog(SearchableText='\303\226ffin')
        self.assertEqual(len(brains), 1)

    def testQueryDifferentiatesUmlautsLower(self):
        self.doc1.SearchableText = '\303\204ffin'
        self.catalog.indexObject(self.doc1)
        self.doc2.SearchableText = '\303\226ffin'
        self.catalog.indexObject(self.doc2)
        brains = self.catalog(SearchableText='\303\266ffin')
        self.assertEqual(len(brains), 1)

    def testQueryByLatin1(self):
        #
        # Test passes because plone_lexicon pipeline elements
        # are coded defensively.
        #
        saved = _setlocale(*LATIN1)
        try:
            self.doc1.SearchableText = '\xc4ffin'
            self.catalog.indexObject(self.doc1)
            brains = self.catalog(SearchableText='\xc4ffin')
            self.assertEqual(len(brains), 1)
        finally:
            _setlocale(saved)

    def testQueryByLatin1Lower(self):
        #
        # Test passes because plone_lexicon pipeline elements
        # are coded defensively.
        #
        saved = _setlocale(*LATIN1)
        try:
            self.doc1.SearchableText = '\xc4ffin'
            self.catalog.indexObject(self.doc1)
            brains = self.catalog(SearchableText='\xe4ffin')
            self.assertEqual(len(brains), 1)
        finally:
            _setlocale(saved)

    def testMixedModeQuery(self):
        #
        # Test passes because plone_lexicon pipeline elements
        # are coded defensively.
        #
        saved = _setlocale(*LATIN1)
        try:
            # Index Latin-1
            self.doc1.SearchableText = '\xc4ffin'
            self.catalog.indexObject(self.doc1)
            # Query by UTF-8
            brains = self.catalog(SearchableText='\303\204ffin')
            # We get no results, but at least we don't break
            self.assertEqual(len(brains), 0)
        finally:
            _setlocale(saved)

    def testQueryByUnicode(self):
        self.doc1.SearchableText = '\303\204ffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText=u'\xc4ffin')
        self.assertEqual(len(brains), 1)

    def testQueryByUnicodeLower(self):
        self.doc1.SearchableText = '\303\204ffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText=u'\xe4ffin')
        self.assertEqual(len(brains), 1)

    def testIndexUnicode(self):
        self.doc1.SearchableText = u'\xc4ffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='\303\204ffin')
        self.assertEqual(len(brains), 1)

    def testIndexUnicodeLower(self):
        self.doc1.SearchableText = u'\xc4ffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='\303\244ffin')
        self.assertEqual(len(brains), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSplitter))
    suite.addTest(makeSuite(TestCaseNormalizer))
    suite.addTest(makeSuite(TestQuery))
    return suite
