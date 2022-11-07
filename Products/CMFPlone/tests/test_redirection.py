from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zExceptions import NotFound

import unittest


class TestRedirection(unittest.TestCase):
    """Test redirecting and resource directories

    These tests were formerly found in redirection.txt.

    When you try to visit a page that does not exist, Plone helpfully
    shows a link to the parent directory.  Normally this is fine.  But
    Plone expects this parent directory to be a normal folder or something
    similar.  It makes some assumptions there that are not valid when the
    parent is a resource directory.  This gives problems while rendering
    the default error page.  In particular it results in a TypeError:
    getTypeInfo.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = Browser(self.layer["app"])
        # In most cases it is more informative to get the Python traceback, so we tell
        # the browser not to handle errors, but in some tests we will override this.
        self.browser.handleErrors = False
        self.browser.raiseHttpErrors = True
        self.portal = self.layer["portal"]
        self.flag_directory = (
            f"{self.portal.absolute_url()}/++resource++language-flags/"
        )
        # Open the portal site root first.  This may be needed to avoid strange error
        # messages in case something is wrong:
        # ZODB.POSException.ConnectionStateError:
        # Shouldn't load state for persistent.list.PersistentList
        # 0x218f5264c344128e when the connection is closed.
        self.browser.open(self.portal.absolute_url())

    def test_get_existing_resource_file(self):
        # Let's check what happens when we get a file from a resourceDirectory.
        # This flag exists:
        self.browser.open(self.flag_directory + "eu.gif")

    def test_get_non_existing_resource_file(self):
        # This flag does not exist, so it should raise a 404:
        with self.assertRaises(NotFound):
            self.browser.open(self.flag_directory + "nonexisting.gif")

    def test_error_for_non_existing_resource_file(self):
        # The 404 page should not itself give errors.
        self.browser.handleErrors = True
        # On Python 3.11 we must disable raiseHttpErrors, otherwise you trigger a core
        # Python bug.  This seems a test-only problem.  See this issue:
        # https://github.com/plone/Products.CMFPlone/issues/3663
        self.browser.raiseHttpErrors = False
        self.browser.open(self.flag_directory + "nonexisting.gif")
        self.assertEqual(self.browser.headers["Status"], "404 Not Found")
        # It should not give an error while rendering the default error page:
        self.assertNotIn(
            b"the following error occurred while attempting to render the standard "
            b"error message",
            self.browser.contents.lower(),
        )
        # As it is an image, it should return a JSON message
        self.assertIn(b'{"error_type": "NotFound"}', self.browser.contents)

    def test_non_existing_page(self):
        # A non-existing page would return a human readable error page
        self.browser.addHeader("Accept", "text/html")
        self.browser.handleErrors = True
        self.browser.raiseHttpErrors = False
        self.browser.open("http://nohost/plone/non-existing-page")
        self.assertIn("This page does not seem to exist", self.browser.contents)
