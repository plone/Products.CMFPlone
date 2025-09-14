from plone.base.interfaces import ISiteSchema
from plone.registry.interfaces import IRegistry
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
