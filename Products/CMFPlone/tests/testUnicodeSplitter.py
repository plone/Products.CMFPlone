# -*- coding: utf-8 -*-
import unittest
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.UnicodeSplitter import Splitter
from Products.CMFPlone.UnicodeSplitter import CaseNormalizer

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.tests.base.dummy import DummyContent

from OFS.metaconfigure import setDeprecatedManageAddDelete

import locale
LATIN1 = ('en_US.ISO-8859-1', 'en_US.ISO8859-15', 'en_GB.ISO8859-15',
          'de_DE@euro', 'fr_FR@euro', 'nl_NL@euro')


def _setlocale(*names):
    saved = locale.setlocale(locale.LC_ALL)
    for name in names:
        try:
            locale.setlocale(locale.LC_ALL, name)
            break
        except locale.Error, e:
            pass
    else:
        raise e.__class__("Unsupported locale. These tests need at least one "
                          "of the following locales available on your system",
                          str(LATIN1))
    return saved


class TestSplitter(unittest.TestCase):

    def setUp(self):
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
            # If this test is failing, you probably just don't have
            # the latin1 locales generated.  On Ubuntu, this worked:
            #
            # $ sudo locale-gen en_US en_US.ISO-8859-1 en_US.ISO8859-15 en_GB.ISO8859-15 de_DE@euro fr_FR@euro nl_NL@euro
            #
            self.assertEqual(self.process(input), output)
            self.assertEqual(self.processGlob(input), output)
        finally:
            _setlocale(saved)


class TestCaseNormalizer(unittest.TestCase):

    def setUp(self):
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
        setDeprecatedManageAddDelete(DummyContent)
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.folder._setObject('doc1',
            DummyContent('doc1', catalog=self.catalog))
        self.doc1 = self.folder.doc1
        self.folder._setObject('doc2',
            DummyContent('doc2', catalog=self.catalog))
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
            self.assertEqual(len(brains), 1)
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


# adding UnicodeSplitterPatcth
from Products.CMFPlone.UnicodeSplitter \
     import process_str, process_str_post, process_str_glob,\
     process_unicode, process_unicode_glob


class TestBigramFunctions(unittest.TestCase):

    def test_process_str(self):
        lsts = [
            ("日本", ["日本", "本"]),
            ("日", ["日"]),
            ("日本語", ["日本", "本語", "語"]),
            ("日本語python", ["日本", "本語", "語", "python"]),
            ("日本語12345", ["日本", "本語", "語", "12345"]),
            ]
        for lst, rst in lsts:
            self.assertEqual(rst, process_str(lst, "utf8"))

    def test_process_unicode(self):
        lsts = [
            (u"日本", [u"日本", u"本"]),
            (u"日", [u"日"]),
            (u"日本語", [u"日本", u"本語", u"語"]),
            (u"日本語python", [u"日本", u"本語", u"語", u"python"]),
            (u"日本語12345", [u"日本", u"本語", u"語", u"12345"]),
            ]
        for lst, rst in lsts:
            self.assertEqual(rst, list(process_unicode(lst)))

    def test_process_str_glob(self):
        enc = "utf8"
        lsts = [
            ("日本", ["日本"]),
            ("日", ["日*"]),
            ("日本語", ["日本", "本語"]),
            ("日本語python", ["日本", "本語", "語", "python"]),
            ]
        for lst, rst in lsts:
            self.assertEqual(rst, process_str_glob(lst, enc))
            for x, y in zip(rst, process_str_glob(lst, enc)):
                self.assertEqual(x, y)
                self.assertEqual(type(x), type(y))

    def test_process_unicode_glob(self):
        lsts = [
            (u"日本", [u"日本"]),
            (u"日", [u"日*"]),
            (u"日本語", [u"日本", u"本語"]),
            (u"日本語python", [u"日本", u"本語", u"語", u"python"]),
            ]
        for lst, rst in lsts:
            self.assertEqual(rst, list(process_unicode_glob(lst)))
            for x, y in zip(rst, process_unicode_glob(lst)):
                self.assertEqual(x, y)
                self.assertEqual(type(x), type(y))

    def test_process_str_post(self):
        enc = "utf8"
        lsts = [
            ("日本", "日本"),
            ("日本*", "日本"),
            ]
        for lst, rst in lsts:
            self.assertEqual(rst, process_str_post(lst, enc))


class TestSearchingJapanese(PloneTestCase.PloneTestCase):
    """Install Japanese test
    """

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.portal.invokeFactory('Document', 'doc1')
        self.doc1 = getattr(self.portal, 'doc1')
        self.doc1.setTitle("Ploneは素晴らしい。")
        self.doc1.setText("このページは予想している通り、テストです。 Pages Testing.")
        self.doc1.reindexObject()

    def testSearch(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        items1 = catalog(SearchableText="予想")
        self.assertEqual(len(items1), 1)
        items12 = catalog(SearchableText="素晴らしい")
        self.assertEqual(len(items12), 1)
        items13 = catalog(SearchableText="Pages")
        self.assertEqual(len(items13), 1)
        items14 = catalog(SearchableText="ページ")
        self.assertEqual(len(items14), 1)
        items15 = catalog(SearchableText="予想*")
        self.assertEqual(len(items15), 1)
        items16 = catalog(SearchableText=u"予想")
        self.assertEqual(len(items16), 1)
        self.portal.manage_delObjects(['doc1'])
        items2 = catalog(SearchableText="予想")
        self.assertEqual(len(items2), 0)


class TestSearchingUnicodeJapanese(PloneTestCase.PloneTestCase):
    """ Install Unicode Japanese test """
    def afterSetUp(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Document', 'doc1')
        self.doc1 = getattr(self.portal, 'doc1')
        self.doc1.setTitle(u"Ploneは素晴らしい。")
        self.doc1.setText(u"このページは予想している通り、テストです。 Pages Testing.")
        self.doc1.reindexObject()

    def testSearch(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        items1 = catalog(SearchableText=u"予想")
        self.assertEqual(len(items1), 1)
        items12 = catalog(SearchableText=u"素晴らしい")
        self.assertEqual(len(items12), 1)
        items13 = catalog(SearchableText=u"Pages")
        self.assertEqual(len(items13), 1)
        items14 = catalog(SearchableText=u"ページ")
        self.assertEqual(len(items14), 1)
        items15 = catalog(SearchableText=u"予想*")
        self.assertEqual(len(items15), 1)
        items16 = catalog(SearchableText="予想")
        self.assertEqual(len(items16), 1)
        self.portal.manage_delObjects(['doc1'])
        items2 = catalog(SearchableText=u"予想")
        self.assertEqual(len(items2), 0)
