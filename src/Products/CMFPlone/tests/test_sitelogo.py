from plone.base.interfaces import ISiteSchema
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getUtility

import unittest

# Red pixel with filename pixel.png
SITE_LOGO_BASE64 = (
    b"filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgA"
    b"AAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAA"
    b"AAElFTkSuQmCC"
)

SITE_LOGO_HEX = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00"
    b"\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT"
    b"\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d"
    b"\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
)


class SiteLogoFunctionalTest(unittest.TestCase):
    """Test the site logo view."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_sitelogo_view(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        settings.site_logo = SITE_LOGO_BASE64
        view = self.portal.restrictedTraverse("@@site-logo")
        self.assertEqual(view(), SITE_LOGO_HEX)
        view.request.response
        headers = view.request.response
        self.assertEqual(headers["content-type"], "image/png")
        self.assertEqual(headers["content-length"], "69")
        self.assertEqual(
            headers["content-disposition"], "attachment; filename*=UTF-8''pixel.png"
        )


class SiteLogoCachingTest(unittest.TestCase):
    """The versioned URL of the logo is a stable resource, others not."""

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        from plone.testing.zope import Browser
        from Products.CMFPlone.utils import getSiteLogo

        import transaction

        self.portal = self.layer["portal"]
        registry = getUtility(IRegistry)
        registry["plone.site_logo"] = SITE_LOGO_BASE64
        transaction.commit()
        self.logo_url = getSiteLogo()
        self.version = self.logo_url.split("/")[-2]
        self.browser = Browser(self.layer["app"])

    def open(self, url, **headers):
        for name, value in headers.items():
            self.browser.addHeader(name, value)
        self.browser.open(url)
        return self.browser.headers

    def test_versioned_url(self):
        headers = self.open(self.logo_url)
        self.assertEqual(self.browser.contents, SITE_LOGO_HEX)
        self.assertEqual(headers["Content-Type"], "image/png")
        self.assertIn(self.logo_url, headers["Link"])

    def test_url_without_version(self):
        # Old links, and the preview in the control panel of Volto.
        self.open(f"{self.portal.absolute_url()}/@@site-logo/pixel.png")
        self.assertEqual(self.browser.contents, SITE_LOGO_HEX)

    def test_url_with_old_version(self):
        self.open(
            f"{self.portal.absolute_url()}/@@site-logo/0123456789abcdef/pixel.png"
        )
        self.assertEqual(self.browser.contents, SITE_LOGO_HEX)

    def test_new_logo_new_url(self):
        from Products.CMFPlone.utils import getSiteLogo

        import transaction

        registry = getUtility(IRegistry)
        registry["plone.site_logo"] = SITE_LOGO_BASE64.replace(b"wAAA", b"wAAB")
        transaction.commit()
        self.assertNotEqual(getSiteLogo(), self.logo_url)

    def test_too_many_path_segments(self):
        from zExceptions import NotFound

        self.browser.handleErrors = False
        with self.assertRaises(NotFound):
            self.open(f"{self.logo_url}/extra")

    def test_caching_rulesets(self):
        # With plone.app.caching, the versioned URL is a stable resource,
        # the others are revalidated like files.
        from z3c.caching.registry import lookup

        request = self.layer["request"]
        view = self.portal.restrictedTraverse("@@site-logo")
        view.publishTraverse(request, self.version)
        view.publishTraverse(request, "pixel.png")
        self.assertEqual(lookup(view), "plone.stableResource")

        view = self.portal.restrictedTraverse("@@site-logo")
        view.publishTraverse(request, "pixel.png")
        self.assertEqual(lookup(view), "plone.content.file")


class SiteLogoNoLogoTest(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def test_no_logo(self):
        from zExceptions import NotFound

        view = self.layer["portal"].restrictedTraverse("@@site-logo")
        with self.assertRaises(NotFound):
            view()
