from lxml import etree
from plone.testing.zope import Browser
from Products.CMFPlone.browser.icons import _add_aria_title
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import io
import unittest


class IconsTest(unittest.TestCase):
    """Test the icon resolver view."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

    def test_icons_browser(self):
        browser = Browser(self.app)
        portal_url = self.portal.absolute_url()
        url = portal_url + "/@@iconresolver/bug"
        browser.open(url)
        # Calling the @@iconresolver/bug url directly will lead ZPublisher
        # HTTPResponse add the image/svg+xml mimetype to the response header
        # and encode the body as bytes.
        self.assertIn(b"bi bi-bug", browser.contents)

    def test_icons_view(self):
        page = self.app
        view = page.restrictedTraverse("@@iconresolver")
        self.assertIn("bi bi-bug", view.tag("bug"))

    def test_icons_url(self):
        page = self.app
        view = page.restrictedTraverse("@@iconresolver")
        self.assertIn("++plone++bootstrap-icons/bug.svg", view.url("bug"))

    def test_icons_tag(self):
        page = self.app
        view = page.restrictedTraverse("@@iconresolver")
        self.assertIn("bi bi-bug", view.tag("bug"))


class IconTraverserTest(unittest.TestCase):
    """Test the icon traverser or PloneBundlesTraverser."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_default_icon(self):
        self.portal.restrictedTraverse("++plone++icons/plone.svg")

    def test_bootstrap_icon(self):
        self.portal.restrictedTraverse("++plone++bootstrap-icons/clock.svg")

    def test_bootstrap_icon_with_path_info(self):
        """Get bootstrap icon while request has a PATH_INFO.

        When the request has PATH_INFO, which it normally has,
        the code originally ignored the remaining name (clock.svg)
        and tried to traverse based on this PATH_INFO.
        This works fine when the url of the request is for an icon.
        But when the url is for a normal page which tries to load an icon
        in the template, it fails.

        I don't know why most of the time it goes right.
        But I have occasionally seen failures.
        And it happens at least in plone.i18n tests.
        https://github.com/plone/plone.i18n/pull/41
        """
        self.request.environ["PATH_INFO"] = "plone"
        self.portal.restrictedTraverse("++plone++bootstrap-icons/clock.svg")


class SVGAriaTest(unittest.TestCase):
    """The aria attributes put on SVG icons by the icon resolver.

    These exercise the modifier directly, so they need no Plone layer.
    """

    SVG = (
        b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
        b'<path d="M0 0h16v16H0z"/></svg>'
    )

    def _modify(self, cfg, svg=None):
        tree = etree.parse(io.BytesIO(svg or self.SVG))
        _add_aria_title(tree, cfg)
        return tree.getroot()

    def test_icon_is_hidden_from_assistive_technology(self):
        # Icons are always rendered beside their own text label, so they are
        # decorative and must not be announced.
        root = self._modify({"title": "Bug"})
        self.assertEqual(root.attrib.get("aria-hidden"), "true")

    def test_icon_without_title_is_also_hidden(self):
        root = self._modify({"title": ""})
        self.assertEqual(root.attrib.get("aria-hidden"), "true")

    def test_broken_aria_labelledby_is_not_emitted(self):
        # Regression for #3394: this pointed at id="title", which was never
        # set -- and _strip_id removes all ids anyway.
        root = self._modify({"title": "Bug"})
        self.assertNotIn("aria-labelledby", root.attrib)

    def test_existing_aria_labelledby_is_removed(self):
        svg = (
            b'<svg xmlns="http://www.w3.org/2000/svg" aria-labelledby="title">'
            b"</svg>"
        )
        root = self._modify({"title": "Bug"}, svg)
        self.assertNotIn("aria-labelledby", root.attrib)

    def test_title_is_kept_for_the_hover_tooltip(self):
        root = self._modify({"title": "Bug"})
        title = root.find("{http://www.w3.org/2000/svg}title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, "Bug")

    def test_no_title_tag_when_no_alt_given(self):
        root = self._modify({"title": ""})
        self.assertIsNone(root.find("{http://www.w3.org/2000/svg}title"))

    def test_title_is_not_duplicated_on_a_second_pass(self):
        # The title is created in the SVG namespace, so the lookup finds it
        # again instead of appending a second one.
        tree = etree.parse(io.BytesIO(self.SVG))
        _add_aria_title(tree, {"title": "Bug"})
        _add_aria_title(tree, {"title": "Bug"})
        titles = tree.getroot().findall("{http://www.w3.org/2000/svg}title")
        self.assertEqual(len(titles), 1)

    def test_prefixed_namespace_svg(self):
        # An SVG declaring its namespace with a prefix has no default nsmap
        # entry; the title must still land in the SVG namespace.
        svg = (
            b'<svg:svg xmlns:svg="http://www.w3.org/2000/svg" '
            b'viewBox="0 0 16 16"></svg:svg>'
        )
        root = self._modify({"title": "Bug"}, svg)
        self.assertEqual(root.attrib.get("aria-hidden"), "true")
        title = root.find("{http://www.w3.org/2000/svg}title")
        self.assertIsNotNone(title)
        self.assertEqual(title.text, "Bug")

    def test_serialised_output(self):
        tree = etree.parse(io.BytesIO(self.SVG))
        _add_aria_title(tree, {"title": "Bug"})
        out = etree.tostring(tree).decode()
        self.assertIn('aria-hidden="true"', out)
        self.assertNotIn("aria-labelledby", out)
        self.assertIn("<title>Bug</title>", out)
