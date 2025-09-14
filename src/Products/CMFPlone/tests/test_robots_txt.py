from plone.base.interfaces import ISiteSchema
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import getUtility

import unittest


class RobotsTxtFunctionalTest(unittest.TestCase):
    """Test robots.txt."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_robots_view(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.assertIn("{portal_url}/sitemap.xml.gz", settings.robots_txt)
        view = self.portal.restrictedTraverse("robots.txt")
        self.assertIn("http://nohost/plone/sitemap.xml.gz", view())
        settings.robots_txt = "Dummy"
        self.assertEqual("Dummy", view())
