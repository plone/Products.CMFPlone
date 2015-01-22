# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import unittest2 as unittest

# Red pixel with filename pixel.png
SITE_LOGO_BASE64 = 'filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgAA'\
                   'AAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAAAA'\
                   'ElFTkSuQmCC'
SITE_LOGO_HEX = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'\
                '\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT'\
                '\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d'\
                '\xb0\x00\x00\x00\x00IEND\xaeB`\x82'


class SiteLogoFunctionalTest(unittest.TestCase):
    """Test the site logo view.
    """
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_sitelogo_view(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        settings.site_logo = SITE_LOGO_BASE64
        view = self.portal.restrictedTraverse('@@site-logo')
        self.assertTrue(view(), SITE_LOGO_HEX)
        view.request.response
        headers = view.request.response
        self.assertTrue(headers['content-type'], 'image/png')
        self.assertTrue(headers['content-length'], '69')
        self.assertTrue(
            headers['content-disposition'],
            "attachment; filename*=UTF-8''pixel.png"
        )
