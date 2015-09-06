# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import unittest2 as unittest


class RobotsTxtFunctionalTest(unittest.TestCase):
    """Test robots.txt."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_robots_view(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        self.assertIn('{portal_url}/sitemap.xml.gz', settings.robots_txt)
        view = self.portal.restrictedTraverse('robots.txt')
        self.assertIn('http://nohost/plone/sitemap.xml.gz', view())
        settings.robots_txt = u"Dummy"
        self.assertEqual(u"Dummy", view())
