from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.MailHost.interfaces import IMailHost
from Products.statusmessages.interfaces import IStatusMessage

import unittest
import warnings


class TestPloneTool(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.tool = getToolByName(self.portal, "plone_utils", None)

    def test_getSiteEncoding(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.assertEqual(self.tool.getSiteEncoding(), "utf-8")

    def test_getMailHost(self):
        self.assertTrue(IMailHost.providedBy(self.tool.getMailHost()))

    def test_getReviewStateTitleFor(self):
        folder_id = self.portal.invokeFactory("Folder", "folder")
        folder = self.portal[folder_id]
        self.assertEqual(self.tool.getReviewStateTitleFor(folder).lower(), "private")

    def test_urlparse(self):
        """See Python standard library urlparse.urlparse:
        http://python.org/doc/lib/module-urlparse.html
        """
        url = "http://dev.plone.org/plone/query?milestone=2.1#foo"
        expected = ("http", "dev.plone.org", "/plone/query", "", "milestone=2.1", "foo")
        self.assertEqual(tuple(self.tool.urlparse(url)), expected)

    def test_urlunparse(self):
        """See Python standard library: urlparse.urlunparse:
        http://python.org/doc/lib/module-urlparse.html
        """
        data = ("http", "plone.org", "/support", "", "", "users")
        self.assertEqual(self.tool.urlunparse(data), "http://plone.org/support#users")

    def test_addPortalMessage(self):
        # no status messages
        self.assertEqual(IStatusMessage(self.request).show(), [])

        self.tool.addPortalMessage("A random warning message", "warning")
        status = IStatusMessage(self.request).show()
        self.assertEqual(len(status), 1)
        self.assertEqual(status[0].type, "warning")

        # again no status messages
        self.assertEqual(IStatusMessage(self.request).show(), [])

        self.tool.addPortalMessage("A random info message")
        status = IStatusMessage(self.request).show()
        self.assertEqual(len(status), 1)
        self.assertEqual(status[0].type, "info")

    def test_isStructuralFolder(self):
        folder_id = self.portal.invokeFactory("Folder", "folder")
        folder = self.portal[folder_id]
        self.assertTrue(self.tool.isStructuralFolder(folder))

    def test_getOwnerName(self):
        login(self.portal, TEST_USER_NAME)

        folder_id = self.portal.invokeFactory("Folder", "folder")
        folder = self.portal[folder_id]

        self.assertEqual(self.tool.getOwnerName(folder), TEST_USER_ID)

    def test_normalizeString(self):
        self.assertEqual(self.tool.normalizeString("Foo bar"), "foo-bar")
        self.assertEqual(
            self.tool.normalizeString("Some!_are allowed, others&?:are not"),
            "some-_are-allowed-others-are-not",
        )
        self.assertEqual(
            self.tool.normalizeString("Some!_are allowed, others&?:are not"),
            "some-_are-allowed-others-are-not",
        )

    def test_normalizeString_punctuation_and_spacing(self):
        """all punctuation and spacing is removed and replaced with a '-'"""
        self.assertEqual(
            self.tool.normalizeString("a string with spaces"), "a-string-with-spaces"
        )
        self.assertEqual(
            self.tool.normalizeString("p.u,n;c(t)u!a@t#i$o%n"), "p-u-n-c-t-u-a-t-i-o-n"
        )

    def test_normalizeString_lowercase(self):
        """strings are lowercased"""
        self.assertEqual(self.tool.normalizeString("UppERcaSE"), "uppercase")

    def test_normalizeString_trim_and_reduce(self):
        """punctuation, spaces, etc. are trimmed and multiples are reduced to
        just one
        """
        self.assertEqual(self.tool.normalizeString(" a string    "), "a-string")
        self.assertEqual(self.tool.normalizeString(">here's another!"), "heres-another")

        self.assertEqual(
            self.tool.normalizeString("one with !@#$!@#$ stuff in the middle"),
            "one-with-stuff-in-the-middle",
        )

    def test_normalizeString_file_like(self):
        """the exception to all this is that if there is something that looks
        like a filename with an extension at the end, it will preserve the last
        period.
        """
        self.assertEqual(
            self.tool.normalizeString("this is a file.gif"), "this-is-a-file-gif"
        )

        self.assertEqual(
            self.tool.normalizeString("this is. also. a file.html"),
            "this-is-also-a-file-html",
        )

    def test_getEmptyTitle(self):
        self.assertEqual(self.tool.getEmptyTitle(translated=False), "[\xb7\xb7\xb7]")
