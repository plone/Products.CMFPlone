from OFS.metaconfigure import setDeprecatedManageAddDelete
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield import RichTextValue
from Products.CMFCore.tests.base.dummy import DummyContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
# adding UnicodeSplitterPatcth
from Products.CMFPlone.UnicodeSplitter import CaseNormalizer
from Products.CMFPlone.UnicodeSplitter import process_str
from Products.CMFPlone.UnicodeSplitter import process_str_glob
from Products.CMFPlone.UnicodeSplitter import process_str_post
from Products.CMFPlone.UnicodeSplitter import process_unicode
from Products.CMFPlone.UnicodeSplitter import process_unicode_glob
from Products.CMFPlone.UnicodeSplitter import Splitter

import locale
import unittest


LATIN1 = ('en_US.ISO-8859-1', 'en_US.ISO8859-15', 'en_GB.ISO8859-15',
          'de_DE@euro', 'fr_FR@euro', 'nl_NL@euro')


def _setlocale(*names):
    saved = locale.setlocale(locale.LC_ALL)
    for name in names:
        try:
            locale.setlocale(locale.LC_ALL, name)
            break
        except locale.Error as e:
            pass
    else:
        raise ValueError(
            "Unsupported locale. "
            "These tests need at least one of the following locales "
            "available on your system: %s" % str(LATIN1)
        )
    return saved


class TestSplitter(unittest.TestCase):

    def setUp(self):
        self.splitter = Splitter()
        self.process = self.splitter.process
        self.processGlob = self.splitter.processGlob

    def testProcessGerman(self):
        # German letters
        input = ["\xc4ffin foo"]
        output = ["\xc4ffin", "foo"]
        output = [t.encode('utf-8') for t in output]

        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

        input = [t.encode('utf-8') for t in input]
        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

    def testProcessGreek(self):
        # Greek letters
        input = [
            '\u039d\u03af\u03ba\u03bf\u03c2 \u03a4\u03b6\u03ac\u03bd\u03bf\u03c2 foo']
        output = ['\u039d\u03af\u03ba\u03bf\u03c2',
                  '\u03a4\u03b6\u03ac\u03bd\u03bf\u03c2', 'foo']
        output = [t.encode('utf-8') for t in output]

        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

        input = [t.encode('utf-8') for t in input]
        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

    def testProcessTurkish(self):
        # Turkish letters
        input = ["\xdc\u011f\xfcr foo"]
        output = ["\xdc\u011f\xfcr", "foo"]
        output = [t.encode('utf-8') for t in output]

        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

        input = [t.encode('utf-8') for t in input]
        self.assertEqual(self.process(input), output)
        self.assertEqual(self.processGlob(input), output)

    def testMissingLocaleRaises(self):
        with self.assertRaises(ValueError):
            _setlocale('TLH')  # klingon locale code

    def testProcessLatin1(self):
        #
        # Test passes because plone_lexicon pipeline elements
        # are coded defensively.
        #
        u_input = ["\xc4ffin foo"]
        b_input = [t.encode('utf-8') for t in u_input]
        u_output = ["\xc4ffin", "foo"]
        b_output = [t.encode('utf-8') for t in u_output]

        # May still fail if none of the locales is available
        saved = _setlocale(*LATIN1)
        try:
            # If this test is failing, you probably just don't have
            # the latin1 locales generated.  On Ubuntu, this worked:
            #
            # $ sudo locale-gen en_US en_US.ISO-8859-1 en_US.ISO8859-15 en_GB.ISO8859-15 de_DE@euro fr_FR@euro nl_NL@euro  # noqa: E501
            #
            self.assertEqual(self.process(b_input), b_output)
            self.assertEqual(self.processGlob(b_input), b_output)
        finally:
            _setlocale(saved)


class TestCaseNormalizer(unittest.TestCase):

    def setUp(self):
        self.normalizer = CaseNormalizer()
        self.process = self.normalizer.process

    def testNormalizeGerman(self):
        u_input = ["\xc4ffin"]
        b_input = [t.encode('utf-8') for t in u_input]
        u_output = ["\xe4ffin"]
        b_output = [t.encode('utf-8') for t in u_output]

        self.assertEqual(self.process(u_input), b_output)
        self.assertEqual(self.process(b_input), b_output)

    def testNormalizeLatin1(self):
        #
        # Test passes because plone_lexicon pipeline elements
        # are coded defensively.
        #
        u_input = ["\xc4ffin"]
        b_input = [t.encode('utf-8') for t in u_input]
        u_output = ["\xe4ffin"]
        b_output = [t.encode('utf-8') for t in u_output]

        # May still fail if none of the locales is available
        saved = _setlocale(*LATIN1)
        try:
            self.assertEqual(self.process(b_input), b_output)
        finally:
            _setlocale(saved)


class TestQuery(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.invokeFactory('Folder', 'folder1')
        self.folder = self.portal['folder1']
        setDeprecatedManageAddDelete(DummyContent)
        self.catalog = getToolByName(self.portal, 'portal_catalog')
        self.folder._setObject('doc1',
                               DummyContent('doc1', catalog=self.catalog))
        self.doc1 = self.folder.doc1
        self.folder._setObject('doc2',
                               DummyContent('doc2', catalog=self.catalog))
        self.doc2 = self.folder.doc2

    def testQueryByUmlaut(self):
        self.doc1.SearchableText = 'Äffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='Äffin')
        self.assertEqual(len(brains), 1)

    def testQueryByUmlautLower(self):
        self.doc1.SearchableText = 'Äffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='äffin')
        self.assertEqual(len(brains), 1)

    def testQueryDifferentiatesUmlauts(self):
        self.doc1.SearchableText = 'Äffin'
        self.catalog.indexObject(self.doc1)
        self.doc2.SearchableText = 'Öffin'
        self.catalog.indexObject(self.doc2)
        brains = self.catalog(SearchableText='Öffin')
        self.assertEqual(len(brains), 1)

    def testQueryDifferentiatesUmlautsLower(self):
        self.doc1.SearchableText = 'Äffin'
        self.catalog.indexObject(self.doc1)
        self.doc2.SearchableText = 'Öffin'
        self.catalog.indexObject(self.doc2)
        brains = self.catalog(SearchableText='Öffin')
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
            self.doc1.SearchableText = b'\xc4ffin'.decode('latin1')
            self.catalog.indexObject(self.doc1)
            # Query by UTF-8
            brains = self.catalog(
                SearchableText=b'\xc3\x84ffin'.decode('utf8')
            )
            self.assertEqual(len(brains), 1)
        finally:
            _setlocale(saved)

    def testQueryByUnicode(self):
        self.doc1.SearchableText = 'Äffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='Äffin')
        self.assertEqual(len(brains), 1)

    def testQueryByUnicodeLower(self):
        self.doc1.SearchableText = 'Äffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='äffin')
        self.assertEqual(len(brains), 1)

    def testIndexUnicode(self):
        self.doc1.SearchableText = '\xc4ffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='Äffin')
        self.assertEqual(len(brains), 1)

    def testIndexUnicodeLower(self):
        self.doc1.SearchableText = '\xc4ffin'
        self.catalog.indexObject(self.doc1)
        brains = self.catalog(SearchableText='äffin')
        self.assertEqual(len(brains), 1)


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
            rst = [x.encode('utf8') for x in rst]
            self.assertEqual(rst, process_str(lst, "utf8"))

    def test_process_unicode(self):
        lsts = [
            ("日本", ["日本", "本"]),
            ("日", ["日"]),
            ("日本語", ["日本", "本語", "語"]),
            ("日本語python", ["日本", "本語", "語", "python"]),
            ("日本語12345", ["日本", "本語", "語", "12345"]),
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
            rst = [x.encode('utf8') for x in rst]
            self.assertEqual(rst, process_str_glob(lst, enc))
            for x, y in zip(rst, process_str_glob(lst, enc)):
                self.assertEqual(x, y)
                self.assertEqual(type(x), type(y))

    def test_process_unicode_glob(self):
        lsts = [
            ("日本", ["日本"]),
            ("日", ["日*"]),
            ("日本語", ["日本", "本語"]),
            ("日本語python", ["日本", "本語", "語", "python"]),
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
            rst = rst.encode('utf8')
            self.assertEqual(rst, process_str_post(lst, enc))


class TestSearchingJapanese(unittest.TestCase):
    """Install Japanese test
    """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.doc1 = getattr(self.portal, 'doc1')
        self.doc1.setTitle("Ploneは素晴らしい。")
        text = "このページは予想している通り、テストです。 Pages Testing."
        self.doc1.text = RichTextValue(text, 'text/html', 'text/x-html-safe')
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
        items16 = catalog(SearchableText="予想")
        self.assertEqual(len(items16), 1)
        self.portal.manage_delObjects(['doc1'])
        items2 = catalog(SearchableText="予想")
        self.assertEqual(len(items2), 0)


class TestSearchingUnicodeJapanese(unittest.TestCase):
    """ Install Unicode Japanese test """

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Document', 'doc1')
        self.doc1 = getattr(self.portal, 'doc1')
        self.doc1.setTitle("Ploneは素晴らしい。")
        text = "このページは予想している通り、テストです。 Pages Testing."
        self.doc1.text = RichTextValue(text, 'text/html', 'text/x-html-safe')
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
        items16 = catalog(SearchableText="予想")
        self.assertEqual(len(items16), 1)
        self.portal.manage_delObjects(['doc1'])
        items2 = catalog(SearchableText="予想")
        self.assertEqual(len(items2), 0)
