from DateTime import DateTime
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.base.batch import Batch
from plone.base.utils import safe_bytes
from plone.testing.zope import Browser
from Products.CMFPlone.controlpanel.browser.redirects import RedirectionSet
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import io
import math
import transaction
import unittest


class RedirectionControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the redirection control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization",
            f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}",
        )

    def test_redirection_controlpanel_link(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink("URL Management").click()

    def test_redirection_controlpanel_backlink(self):
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.assertTrue("General" in self.browser.contents)

    def test_redirection_controlpanel_sidebar(self):
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getLink("Site Setup").click()
        self.assertTrue(self.browser.url.endswith("/plone/@@overview-controlpanel"))

    def test_redirection_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="redirection-controlpanel"
        )
        self.assertTrue(view())

    def test_redirection_controlpanel_add_redirect(self):
        storage = getUtility(IRedirectionStorage)
        redirection_path = "/alias-folder"
        target_path = "/test-folder"
        storage_path = "/plone/alias-folder"

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="redirection").value = redirection_path
        self.browser.getControl(name="target_path").value = target_path
        self.browser.getControl(name="form.button.Add").click()

        self.assertTrue(
            storage.has_path(storage_path),
            f'Redirection storage should have path "{storage_path}"',
        )

    def test_redirection_controlpanel_remove_redirects(self):
        storage = getUtility(IRedirectionStorage)
        for i in range(31):
            storage[f"/plone/alias{i}"] = "/plone/test-folder"
        transaction.commit()

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        # A batch of 15 is shown, so some are missing.
        self.assertTrue("/plone/alias1" in self.browser.contents)
        self.assertTrue("/plone/alias10" in self.browser.contents)
        self.assertTrue("/plone/alias19" in self.browser.contents)
        self.assertTrue("/plone/alias2" in self.browser.contents)
        self.assertFalse("/plone/alias29" in self.browser.contents)
        # query aliases starting with /alias2
        self.browser.getControl(name="q").value = "/alias2"
        self.browser.getControl(name="form.button.filter").click()
        self.assertFalse("/plone/alias1" in self.browser.contents)
        self.assertTrue("/plone/alias2" in self.browser.contents)
        self.assertTrue("/plone/alias29" in self.browser.contents)
        # The filter could return one value too much.
        # This tests that we have excludemax=True in the RedirectionSet.
        self.assertFalse("/plone/alias3" in self.browser.contents)
        self.assertFalse("/plone/alias30" in self.browser.contents)
        # Remove two.
        self.browser.getControl(name="redirects:tuple").value = [
            "/plone/alias2",
            "/plone/alias20",
        ]
        self.browser.getControl(name="form.button.Remove").click()
        self.assertFalse("/plone/alias2" in storage)
        self.assertFalse("/plone/alias20" in storage)
        self.assertTrue("/plone/alias1" in storage)
        self.assertTrue("/plone/alias29" in storage)
        self.assertEqual(storage.get("/plone/alias29"), "/plone/test-folder")

    def test_redirection_controlpanel_remove_matching_redirects(self):
        storage = getUtility(IRedirectionStorage)
        for i in range(30):
            storage[f"/plone/alias{i}"] = "/plone/test-folder"
        transaction.commit()

        # Removing matching redirects can only happen when a filter is selected.
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.button.MatchRemove").click()
        self.assertTrue(
            "No alternative urls selected for removal." in self.browser.contents
        )
        self.assertEqual(len(storage), 30)
        # query aliases starting with /alias2
        self.browser.getControl(name="q").value = "/alias2"
        # The filter is immediately taken into account,
        # without first explicitly clicking filter.
        # self.browser.getControl(name='form.button.filter').click()
        self.browser.getControl(name="form.button.MatchRemove").click()
        self.assertEqual(len(storage), 19)
        self.assertFalse("/plone/alias2" in storage)
        self.assertFalse("/plone/alias20" in storage)
        self.assertFalse("/plone/alias29" in storage)
        self.assertTrue("/plone/alias1" in storage)
        self.assertTrue("/plone/alias12" in storage)

    def test_redirection_controlpanel_set(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer["portal"].absolute_url_path()
        now = DateTime("2022-02-03")
        for i in range(1000):
            storage.add(
                f"{portal_path:s}/foo/{str(i):s}",
                f"{portal_path:s}/bar/{str(i):s}",
                now=now,
            )
        redirects = RedirectionSet()
        self.assertEqual(len(redirects), 1000)
        self.assertDictEqual(
            redirects[0],
            {
                "datetime": DateTime("2022-02-03"),
                "manual": False,
                "path": "/foo/0",
                "redirect": f"{portal_path:s}/foo/0",
                "redirect-to": "/bar/0",
            },
        )
        self.assertDictEqual(
            redirects[999],
            {
                "datetime": DateTime("2022-02-03"),
                "manual": False,
                "path": "/foo/999",
                "redirect": f"{portal_path:s}/foo/999",
                "redirect-to": "/bar/999",
            },
        )
        self.assertEqual(len(list(iter(redirects))), 1000)
        self.assertDictEqual(
            list(iter(redirects))[0],
            {
                "datetime": DateTime("2022-02-03"),
                "manual": False,
                "path": "/foo/0",
                "redirect": f"{portal_path:s}/foo/0",
                "redirect-to": "/bar/0",
            },
        )

    def test_redirection_controlpanel_batching(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer["portal"].absolute_url_path()
        for i in range(1000):
            storage.add(
                f"{portal_path:s}/foo/{str(i):s}",
                f"{portal_path:s}/bar/{str(i):s}",
            )
        view = getMultiAdapter(
            (self.layer["portal"], self.layer["request"]),
            name="redirection-controlpanel",
        )
        # Test that view/redirects returns batch
        self.assertIsInstance(view.redirects(), Batch)

        # Test that view/batching returns batching with anchor in urls
        batching = view.batching()
        self.assertIn("?b_start:int=990#manage-existing-aliases", batching)

    def test_redirection_controlpanel_redirect_alias_exists(self):
        path_alias = "/alias"
        path_target = "/test-folder"
        storage_alias = f"/plone{path_alias}"
        storage_target = f"/plone{path_target}"
        storage = getUtility(IRedirectionStorage)
        storage.add(storage_alias, storage_target)
        transaction.commit()

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="redirection").value = path_alias
        self.browser.getControl(name="target_path").value = path_target
        self.browser.getControl(name="form.button.Add").click()

        self.assertTrue(
            storage.get(storage_alias) == storage_target,
            f"{storage_target} not target of alternative url!",
        )
        self.assertTrue(
            "The provided alternative url already exists!" in self.browser.contents,
            'Message "alternative url already exists" not in page!',
        )

    def test_redirection_controlpanel_filtering(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer["portal"].absolute_url_path()
        for i in range(1000):
            storage.add(
                f"{portal_path:s}/foo1/{str(i):s}",
                f"{portal_path:s}/bar/{str(i):s}",
            )
        for i in range(1000):
            storage.add(
                f"{portal_path:s}/foo2/{str(i):s}",
                f"{portal_path:s}/bar/{str(i):s}",
            )

        redirects = RedirectionSet()
        self.assertEqual(len(redirects), 2000)
        redirects = RedirectionSet(query="/foo")
        self.assertEqual(len(redirects), 2000)
        redirects = RedirectionSet(query="/foo1")
        self.assertEqual(len(redirects), 1000)
        redirects = RedirectionSet(query="/foo2")
        self.assertEqual(len(redirects), 1000)
        # this should return one and not two (we need excludemax=True)
        redirects = RedirectionSet(query="/foo1/777")
        self.assertEqual(len(redirects), 1)
        # query without an initial slash matches any substring
        redirects = RedirectionSet(query="999")
        self.assertEqual(len(redirects), 2)

        request = self.layer["request"].clone()
        request.form["q"] = "/foo"
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(2000 / 15.0))

        request = self.layer["request"].clone()
        request.form["q"] = "/foo1"
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(1000 / 15.0))

        request = self.layer["request"].clone()
        request.form["q"] = "/foo2"
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(1000 / 15.0))

        request = self.layer["request"].clone()
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(2000 / 15.0))

        # Filtering without new request does not have effect because memoize
        request.form["q"] = "/foo2"
        self.assertEqual(view.redirects().numpages, math.ceil(2000 / 15.0))

    def test_redirection_controlpanel_filter_manual(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer["portal"].absolute_url_path()
        for i in range(100):
            storage.add(
                f"{portal_path:s}/foo/{str(i):s}",
                f"{portal_path:s}/bar/{str(i):s}",
                manual=False,
            )
        for i in range(100, 300):
            storage.add(
                f"{portal_path:s}/foo/{str(i):s}",
                f"{portal_path:s}/bar/{str(i):s}",
                manual=True,
            )

        redirects = RedirectionSet()
        self.assertEqual(len(redirects), 300)
        # Form has yes, no, or empty string, anything else is ignored
        # (so treated as empty string).
        redirects = RedirectionSet(manual="yes")
        self.assertEqual(len(redirects), 200)
        redirects = RedirectionSet(manual="no")
        self.assertEqual(len(redirects), 100)
        redirects = RedirectionSet(manual="")
        self.assertEqual(len(redirects), 300)
        redirects = RedirectionSet(manual="badvalue")
        self.assertEqual(len(redirects), 300)

        request = self.layer["request"].clone()
        request.form["manual"] = ""
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(300 / 15.0))

        request = self.layer["request"].clone()
        request.form["manual"] = "yes"
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(200 / 15.0))

        request = self.layer["request"].clone()
        request.form["manual"] = "no"
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(100 / 15.0))

    def test_redirection_controlpanel_filter_date(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer["portal"].absolute_url_path()
        time0 = DateTime("2001-01-01")
        for i in range(400):
            storage.add(
                f"{portal_path:s}/foo/{str(i):s}",
                f"{portal_path:s}/bar/{str(i):s}",
                now=time0 + i,
            )

        redirects = RedirectionSet()
        self.assertEqual(len(redirects), 400)
        # created can be anything that can be parsed by DateTime. (deprecated)
        # Otherwise it is ignored.
        self.assertEqual(len(RedirectionSet(created="2019-01-01")), 400)
        self.assertEqual(len(RedirectionSet(created="1999-01-01")), 0)
        self.assertEqual(len(RedirectionSet(created="2001-01-01")), 0)
        self.assertEqual(len(RedirectionSet(created="2001-01-02")), 1)
        self.assertEqual(len(RedirectionSet(created="2001-02-01")), 31)
        self.assertEqual(len(RedirectionSet(created="2001-02-01 00:00:00")), 31)
        self.assertEqual(len(RedirectionSet(created="2001-02-01 00:00:01")), 32)
        self.assertEqual(len(RedirectionSet(created="badvalue")), 400)
        # start is inclusive and can be anything that can be parsed by DateTime.
        # Otherwise it is ignored.
        self.assertEqual(len(RedirectionSet(start="2019-01-01")), 0)
        self.assertEqual(len(RedirectionSet(start="2001-01-02")), 399)
        self.assertEqual(len(RedirectionSet(start="2001-02-01 00:00:00")), 369)
        self.assertEqual(len(RedirectionSet(start="2001-02-01 00:00:01")), 368)
        self.assertEqual(len(RedirectionSet(start="badvalue")), 400)

        # End is exclisive and can be anything that can be parsed by DateTime.
        # Otherwise it is ignored.
        self.assertEqual(len(RedirectionSet(end="1999-01-01")), 0)
        self.assertEqual(len(RedirectionSet(end="2000-01-01")), 0)
        self.assertEqual(len(RedirectionSet(end="2001-02-01")), 31)
        self.assertEqual(len(RedirectionSet(end="2001-02-01 00:00:00")), 31)
        self.assertEqual(len(RedirectionSet(end="2001-02-01 00:00:01")), 32)
        self.assertEqual(len(RedirectionSet(end="badvalue")), 400)

        self.assertEqual(len(RedirectionSet(start="2001-01-01", end="2001-01-01")), 0)
        self.assertEqual(len(RedirectionSet(start="2001-01-01", end="2001-01-02")), 1)

        # DateTime('2002-01-01') results in a timezone GMT+0
        self.assertEqual(len(RedirectionSet(end="2002-01-01")), 365)
        # DateTime('2002/01/01') results in a timezone GMT+1 for me,
        # or a different zone depending on where in the world you are.
        # So we need to be lenient in the tests.
        self.assertGreaterEqual(len(RedirectionSet(end="2002/01/01")), 364)
        self.assertLessEqual(len(RedirectionSet(end="2002/01/01")), 366)

        request = self.layer["request"].clone()
        request.form["start"] = ""
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(400 / 15.0))

        request = self.layer["request"].clone()
        request.form["end"] = "2001-01-27"
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(27 / 15.0))

        request = self.layer["request"].clone()
        request.form["end"] = "2002-01-01"
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(365 / 15.0))

        request = self.layer["request"].clone()
        request.form["end"] = "2019-01-01"
        view = getMultiAdapter(
            (self.layer["portal"], request), name="redirection-controlpanel"
        )
        self.assertEqual(view.redirects().numpages, math.ceil(400 / 15.0))

    def test_redirection_controlpanel_redirect_no_target(self):
        path_alias = "/alias"
        path_target = "/not-existing"

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="redirection").value = path_alias
        self.browser.getControl(name="target_path").value = path_target
        self.browser.getControl(name="form.button.Add").click()

        self.assertTrue(
            "The provided target object does not exist." in self.browser.contents,
            'Message "target does not exist" not in page!',
        )

    def test_redirection_controlpanel_missing_slash_target(self):
        path_alias = "/alias"
        path_target = "Members"

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="redirection").value = path_alias
        self.browser.getControl(name="target_path").value = path_target
        self.browser.getControl(name="form.button.Add").click()

        self.assertTrue(
            "Target path must start with a slash." in self.browser.contents,
            "Errormessage for missing slash on target path missing",
        )

    def test_redirection_controlpanel_missing_slash_alias(self):
        path_alias = "alias"
        path_target = "/Members"

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="redirection").value = path_alias
        self.browser.getControl(name="target_path").value = path_target
        self.browser.getControl(name="form.button.Add").click()

        self.assertTrue(
            "Alternative url path must start with a slash." in self.browser.contents,
            "Errormessage for missing slash on alternative url missing",
        )

    def test_manage_aliases_standard(self):
        storage = getUtility(IRedirectionStorage)
        folder = self.portal["test-folder"]

        self.browser.open("%s/@@manage-aliases" % folder.absolute_url())
        self.browser.getControl(name="redirection").value = "/alias"
        self.browser.getControl(name="form.button.Add").click()

        self.assertTrue(
            "Alternative url added." in self.browser.contents,
            "Message for added alternative url missing",
        )
        self.assertTrue(storage.has_path("/plone/alias"))
        self.assertEqual(storage.get("/plone/alias"), "/plone/test-folder")

    def test_manage_aliases_remove(self):
        storage = getUtility(IRedirectionStorage)
        folder = self.portal["test-folder"]
        storage["/plone/alias1"] = "/plone/test-folder"
        storage["/plone/alias2"] = "/plone/test-folder"
        storage["/plone/alias3"] = "/plone/test-folder"
        transaction.commit()

        self.browser.open("%s/@@manage-aliases" % folder.absolute_url())
        self.browser.getControl(name="redirects:tuple").value = [
            "/plone/alias1",
            "/plone/alias2",
        ]
        self.browser.getControl(name="form.button.Remove").click()

        self.assertTrue(
            "Alternative urls removed." in self.browser.contents,
            "Message for removed alternative url missing",
        )
        self.assertFalse("/plone/alias1" in storage)
        self.assertFalse("/plone/alias2" in storage)
        self.assertTrue("/plone/alias3" in storage)
        self.assertEqual(storage.get("/plone/alias3"), "/plone/test-folder")

    def test_manage_aliases_navigation_root(self):
        from plone.app.layout.navigation.interfaces import INavigationRoot
        from zope.interface import alsoProvides

        storage = getUtility(IRedirectionStorage)
        folder = self.portal["test-folder"]
        alsoProvides(folder, INavigationRoot)
        transaction.commit()

        self.browser.open("%s/@@manage-aliases" % folder.absolute_url())
        self.browser.getControl(name="redirection").value = "/alias"
        self.browser.getControl(name="form.button.Add").click()

        self.assertTrue(
            "Alternative url added." in self.browser.contents,
            "Message for added alternative url missing",
        )
        self.assertTrue(storage.has_path("/plone/test-folder/alias"))
        self.assertEqual(storage.get("/plone/test-folder/alias"), "/plone/test-folder")

        # Add the navigation root path explicitly.
        self.browser.getControl(name="redirection").value = "/test-folder/alias2"
        self.browser.getControl(name="form.button.Add").click()

        self.assertTrue(
            "Alternative url added." in self.browser.contents,
            "Message for added alternative url missing",
        )
        self.assertTrue(storage.has_path("/plone/test-folder/alias2"))
        self.assertEqual(storage.get("/plone/test-folder/alias2"), "/plone/test-folder")

    def test_absolutize_path(self):
        # absolutize_path is a helper function that returns a tuple
        # of absolute path and error message.
        from Products.CMFPlone.controlpanel.browser.redirects import (
            absolutize_path as ap,
        )

        # A path is required.
        self.assertEqual(ap(""), ("", "You have to enter an alternative url."))
        self.assertEqual(ap("", is_source=False), ("", "You have to enter a target."))

        # relative paths are not accepted
        self.assertEqual(
            ap("foo"), ("foo", "Alternative url path must start with a slash.")
        )
        self.assertEqual(
            ap("foo", is_source=True),
            ("foo", "Alternative url path must start with a slash."),
        )
        self.assertEqual(
            ap("foo", is_source=False),
            ("foo", "Target path must start with a slash."),
        )

        # absolute paths are good
        self.assertEqual(ap("/foo"), ("/plone/foo", None))
        self.assertEqual(ap("/foo", is_source=True), ("/plone/foo", None))

        # for targets, an object must exist on the path
        self.assertEqual(
            ap("/foo", is_source=False),
            ("/plone/foo", "The provided target object does not exist."),
        )
        self.assertEqual(
            ap("/test-folder", is_source=False), ("/plone/test-folder", None)
        )
        self.assertEqual(
            ap("/test-folder/@@sharing", is_source=False),
            ("/test-folder/@@sharing", "Target path must not be a view."),
        )

        # A source must not exist.
        self.assertEqual(
            ap("/test-folder"),
            (
                "/plone/test-folder",
                "Cannot use a working path as alternative url.",
            ),
        )
        # More general: a source must not be traversable already.
        self.assertEqual(
            ap("/view"),
            ("/plone/view", "Cannot use a working path as alternative url."),
        )
        self.assertEqual(
            ap("/@@overview-controlpanel"),
            (
                "/@@overview-controlpanel",
                "Alternative url path must not be a view.",
            ),
        )

        # And a source must not exist via (implicit) acquisition.
        # We might *want* to allow this, but such a redirect would not have effect,
        # because acquisition happens earlier.
        # See https://github.com/collective/Products.RedirectionTool/issues/12
        self.portal.invokeFactory("Document", "doc")
        self.assertEqual(
            ap("/test-folder/doc"),
            (
                "/plone/test-folder/doc",
                "Cannot use a working path as alternative url.",
            ),
        )

        # A source must not already exist in the redirect list.
        storage = getUtility(IRedirectionStorage)
        portal_path = self.portal.absolute_url_path()
        storage.add(
            f"{portal_path:s}/foo",
            f"{portal_path:s}/test-folder",
        )
        self.assertEqual(
            ap("/foo", is_source=True),
            ("/plone/foo", "The provided alternative url already exists!"),
        )

        # For targets, we now accept external urls.
        # Note that this can only be done on the control panel,
        # so by default only by Site Administrators or Managers.
        self.assertEqual(
            ap("https://example.org", is_source=False),
            ("https://example.org", None),
        )
        self.assertEqual(
            ap("http://example.org", is_source=False),
            ("http://example.org", None),
        )
        self.assertEqual(
            ap(
                "https://example.org/some/path?foo=bar&bar=foo",
                is_source=False,
            ),
            ("https://example.org/some/path?foo=bar&bar=foo", None),
        )
        self.assertEqual(
            ap("http://", is_source=False),
            ("http://", "Target path must start with a slash."),
        )
        # Using '//' to ignore http/https differences seems useless,
        # as we don't include content but only link to it.
        self.assertEqual(
            ap("//example.org", is_source=False),
            (
                "/plone//example.org",
                "The provided target object does not exist.",
            ),
        )

    def test_upload_two_columns(self):
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        # Note: the targets must exist as actual content.
        data = [
            (b"/old-home-page.asp", b"/test-folder"),
            (b"/people/JoeT", b"/Members"),
        ]
        csv = b"\n".join([b",".join(d) for d in data])
        self.browser.getControl(name="file").add_file(
            io.BytesIO(csv), "text/plain", "redirects.csv"
        )
        self.browser.getControl(name="form.button.Upload").click()
        self.assertNotIn("Please pick a file to upload.", self.browser.contents)
        self.assertNotIn("No alternative urls were added.", self.browser.contents)
        self.assertNotIn("Please correct these errors", self.browser.contents)
        storage = getUtility(IRedirectionStorage)
        self.assertEqual(len(storage), 2)
        self.assertEqual(storage.get("/plone/old-home-page.asp"), "/plone/test-folder")
        self.assertEqual(storage.get("/plone/people/JoeT"), "/plone/Members")
        # Test the internals.
        redirect = storage._paths["/plone/old-home-page.asp"]
        self.assertEqual(redirect[0], "/plone/test-folder")
        self.assertIsInstance(redirect[1], DateTime)
        self.assertEqual(redirect[2], True)  # manual

    def test_upload_four_columns(self):
        # Two columns are the minimum,
        # but we can handle a third column with a datetime,
        # a fourth column with manual True/False,
        # and more columns that we ignore.
        now = DateTime()
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        # Note: the targets must exist as actual content.
        data = [
            # We can first have a header, which should be ignored.
            # Second one should have the same number of columns,
            # otherwise the delimiter detection can get it wrong.
            (b"old path", b"new path", b"datetime", b"manual"),
            # bad dates are silently ignored
            (b"/baddate", b"/test-folder", b"2006-13-62", b"yes"),
            # two columns:
            (b"/two", b"/test-folder"),
            # third column with date:
            (b"/three", b"/test-folder", b"2003-01-31"),
            # fourth column with manual:
            (
                b"/four",
                b"/test-folder",
                b"2004/01/27 10:00:00 GMT-3",
                b"False",
            ),
            # fifth column is ignored:
            (b"/five", b"/test-folder", b"2005-01-31", b"True", b"ignored"),
            # manual can be '0' (or anything starting with f/F/n/N/0)
            (b"/zero", b"/test-folder", b"2000-01-31", b"0"),
        ]
        csv = b"\n".join([b",".join(d) for d in data])
        self.browser.getControl(name="file").add_file(
            io.BytesIO(csv), "text/plain", "redirects.csv"
        )
        self.browser.getControl(name="form.button.Upload").click()
        self.assertNotIn("Please pick a file to upload.", self.browser.contents)
        self.assertNotIn("No alternative urls were added.", self.browser.contents)
        self.assertNotIn("Please correct these errors", self.browser.contents)

        # All five lines have been added.
        storage = getUtility(IRedirectionStorage)
        self.assertEqual(len(storage), 6)
        self.assertEqual(storage.get("/plone/two"), "/plone/test-folder")
        old_paths = [
            "/plone/baddate",
            "/plone/five",
            "/plone/four",
            "/plone/three",
            "/plone/two",
            "/plone/zero",
        ]
        self.assertListEqual(sorted(list(storage)), old_paths)
        self.assertListEqual(
            sorted(list(storage.redirects("/plone/test-folder"))), old_paths
        )
        # Test the internals.

        # two columns:
        # (b'/two', b'/test-folder'),
        redirect = storage._paths["/plone/two"]
        self.assertEqual(redirect[0], "/plone/test-folder")
        self.assertIsInstance(redirect[1], DateTime)
        self.assertGreater(redirect[1], now)
        self.assertEqual(redirect[2], True)  # manual

        # third column with date:
        # (b'/three', b'/test-folder', b'2003-01-31'),
        redirect = storage._paths["/plone/three"]
        self.assertEqual(redirect[0], "/plone/test-folder")
        self.assertEqual(redirect[1], DateTime("2003-01-31"))
        self.assertEqual(redirect[2], True)

        # fourth column with manual:
        # (b'/four', b'/test-folder', b'2004/01/27 10:00:00 GMT-3', b'False'),
        redirect = storage._paths["/plone/four"]
        self.assertEqual(redirect[0], "/plone/test-folder")
        self.assertEqual(redirect[1], DateTime("2004/01/27 10:00:00 GMT-3"))
        self.assertEqual(redirect[2], False)

        # fifth column is ignored:
        # (b'/five', b'/test-folder', b'2005-01-31', b'True', b'ignored'),
        redirect = storage._paths["/plone/five"]
        self.assertEqual(redirect[0], "/plone/test-folder")
        self.assertEqual(redirect[1], DateTime("2005-01-31"))
        self.assertEqual(redirect[2], True)

        # manual can be '0' (or anything starting with f/F/n/N/0)
        # (b'/zero', b'/test-folder', b'2000-01-31', b'0'),
        redirect = storage._paths["/plone/zero"]
        self.assertEqual(redirect[0], "/plone/test-folder")
        self.assertEqual(redirect[1], DateTime("2000-01-31"))
        self.assertEqual(redirect[2], False)

        # bad dates are silently ignored
        # (b'/baddate', b'/test-folder', b'2006-13-62', b'yes'),
        redirect = storage._paths["/plone/baddate"]
        self.assertEqual(redirect[0], "/plone/test-folder")
        self.assertGreater(redirect[1], now)
        self.assertEqual(redirect[2], True)

    def test_upload_bad(self):
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        # The targets must exist as actual content.
        # We try a good one and one that does not exist.
        data = [
            (b"/old-home-page.asp", b"/test-folder"),
            (b"/people/JoeT", b"/no-such-content"),
        ]
        csv = b"\n".join([b",".join(d) for d in data])
        self.browser.getControl(name="file").add_file(
            io.BytesIO(csv), "text/plain", "redirects.csv"
        )
        self.browser.getControl(name="form.button.Upload").click()
        self.assertNotIn("Please pick a file to upload.", self.browser.contents)
        self.assertIn("No alternative urls were added.", self.browser.contents)
        self.assertIn("Please correct these errors", self.browser.contents)
        storage = getUtility(IRedirectionStorage)
        self.assertEqual(len(storage), 0)

    def test_download_empty(self):
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.button.Download").click()
        self.assertEqual(
            self.browser.headers["Content-Disposition"],
            "attachment; filename=redirects.csv",
        )
        contents = self.browser.contents.splitlines()
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0], "old path,new path,datetime,manual")

    def test_download_bigger(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer["portal"].absolute_url_path()
        now = DateTime("2019/01/27 10:00:00 GMT-3")
        for i in range(2000):
            storage.add(
                f"{portal_path:s}/foo/{str(i):s}",
                f"{portal_path:s}/bar/{str(i):s}",
                now=now,
                manual=True,
            )
        transaction.commit()
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.button.Download").click()
        self.assertEqual(
            self.browser.headers["Content-Disposition"],
            "attachment; filename=redirects.csv",
        )
        contents = self.browser.contents.splitlines()
        # pop the header
        self.assertEqual(contents.pop(0), "old path,new path,datetime,manual")
        self.assertEqual(len(contents), 2000)
        # The order is probably the alphabetical order of the old path,
        # but that is not important and may change,
        # so let's sort it in the tests for good measure.
        # Note that '999' sorts alphabetically after '1999'.
        contents.sort()
        self.assertEqual(contents[0], "/foo/0,/bar/0,2019/01/27 10:00:00 GMT-3,True")
        self.assertEqual(
            contents[1999], "/foo/999,/bar/999,2019/01/27 10:00:00 GMT-3,True"
        )

    def test_download_upload(self):
        # Test uploading a download and downloading an upload.

        # 1. Manually add some redirects.
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer["portal"].absolute_url_path()
        now = DateTime("2019/01/27 10:00:00 GMT-3")
        for i in range(10):
            storage.add(
                f"{portal_path:s}/foo/{str(i):s}",
                f"{portal_path:s}/test-folder",
                now=now,
                manual=True,
            )
        transaction.commit()

        # 2. Download the redirects.
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.button.Download").click()
        self.assertEqual(
            self.browser.headers["Content-Disposition"],
            "attachment; filename=redirects.csv",
        )
        downloaded_contents = self.browser.contents
        contents = downloaded_contents.splitlines()
        self.assertEqual(contents.pop(0), "old path,new path,datetime,manual")
        self.assertEqual(len(contents), 10)
        contents.sort()
        self.assertEqual(
            contents[0], "/foo/0,/test-folder,2019/01/27 10:00:00 GMT-3,True"
        )

        # 3. clear the redirect storage
        storage.clear()
        transaction.commit()
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="form.button.Download").click()
        contents = self.browser.contents.splitlines()
        self.assertEqual(len(contents), 1)
        self.assertEqual(contents[0], "old path,new path,datetime,manual")

        # 4. upload the original download
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name="file").add_file(
            io.BytesIO(safe_bytes(downloaded_contents)),
            "text/plain",
            "redirects.csv",
        )
        self.browser.getControl(name="form.button.Upload").click()
        self.assertNotIn("Please pick a file to upload.", self.browser.contents)
        self.assertNotIn(
            "The provided target object does not exist.", self.browser.contents
        )
        self.assertNotIn("No alternative urls were added.", self.browser.contents)
        self.assertNotIn("Please correct these errors", self.browser.contents)
        self.assertEqual(len(storage), 10)

        # 5. download the upload
        self.browser.getControl(name="form.button.Download").click()
        new_downloaded_contents = self.browser.contents
        contents = downloaded_contents.splitlines()
        self.assertEqual(contents.pop(0), "old path,new path,datetime,manual")
        self.assertEqual(len(contents), 10)
        contents.sort()
        self.assertEqual(
            contents[0], "/foo/0,/test-folder,2019/01/27 10:00:00 GMT-3,True"
        )
        # and it is actually the same as the original download
        self.assertEqual(new_downloaded_contents, downloaded_contents)
