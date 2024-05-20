""" Unit tests for utils module. """

from plone.base.interfaces import ISiteSchema
from plone.registry.interfaces import IRegistry
from Products.CMFCore.tests.base.content import FAUX_HTML_LEADING_TEXT
from Products.CMFCore.tests.base.content import SIMPLE_HTML
from Products.CMFCore.tests.base.content import SIMPLE_STRUCTUREDTEXT
from Products.CMFCore.tests.base.content import SIMPLE_XHTML
from Products.CMFCore.tests.base.content import STX_WITH_HTML
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getUtility

import unittest


SITE_LOGO_BASE64 = (
    b"filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgA"
    b"AAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAA"
    b"AAElFTkSuQmCC"
)


class DefaultUtilsTests(unittest.TestCase):
    def test_bodyfinder(self):
        from Products.CMFPlone.utils import bodyfinder

        self.assertEqual(
            bodyfinder(FAUX_HTML_LEADING_TEXT), "\n  <h1>Not a lot here</h1>\n "
        )
        self.assertEqual(bodyfinder(SIMPLE_HTML), "\n  <h1>Not a lot here</h1>\n ")
        self.assertEqual(bodyfinder(SIMPLE_STRUCTUREDTEXT), SIMPLE_STRUCTUREDTEXT)
        self.assertEqual(bodyfinder(SIMPLE_XHTML), "\n  <h1>Not a lot here</h1>\n ")
        self.assertEqual(bodyfinder(STX_WITH_HTML), "<p>Hello world, I am Bruce.</p>")


class LogoTests(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def test_getSiteLogo_with_setting(self):
        from Products.CMFPlone.utils import getSiteLogo

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        settings.site_logo = SITE_LOGO_BASE64
        logo_url, logo_type = getSiteLogo(include_type=True)

        self.assertTrue("http://nohost/plone/@@site-logo/pixel.png" in logo_url)

        self.assertEqual("image/png", logo_type)

    def test_getSiteLogo_with_no_setting(self):
        from Products.CMFPlone.utils import getSiteLogo

        logo_url, logo_type = getSiteLogo(include_type=True)
        self.assertTrue("http://nohost/plone/++resource++plone-logo.svg" in logo_url)
        self.assertEqual("image/svg+xml", logo_type)
