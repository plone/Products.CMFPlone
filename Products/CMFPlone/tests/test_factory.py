from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.utils import get_installer
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from zope.component import queryUtility

import unittest


class TestFactoryPloneSite(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.request = self.layer['request']

    def testPlonesiteWithUnicodeTitle(self):
        TITLE = 'Ploné'
        ploneSite = addPloneSite(
            self.app, 'ploneFoo', title=TITLE, setup_content=False)
        ploneSiteTitleProperty = ploneSite.getProperty('title')
        # CMF stores title as string only so Plone should keep the same track
        self.assertTrue(isinstance(ploneSiteTitleProperty, str))
        self.assertEqual(ploneSiteTitleProperty, TITLE)
        ploneSiteTitle = ploneSite.Title()
        self.assertTrue(isinstance(ploneSiteTitle, str))
        self.assertEqual(ploneSiteTitle, TITLE)

    def testPlonesiteWithoutUnicodeTitle(self):
        TITLE = 'Plone'
        ploneSite = addPloneSite(
            self.app, 'ploneFoo', title=TITLE, setup_content=False)
        ploneSiteTitleProperty = ploneSite.getProperty('title')
        # CMF stores title as string only so Plone should keep the same track
        self.assertTrue(isinstance(ploneSiteTitleProperty, str))
        self.assertEqual(ploneSiteTitleProperty, TITLE)
        ploneSiteTitle = ploneSite.Title()
        self.assertTrue(isinstance(ploneSiteTitle, str))
        self.assertEqual(ploneSiteTitle, TITLE)

    def test_site_creation_without_content_but_with_dexterity(self):
        """Test site creation without example content have dexterity installed."""
        ploneSite = addPloneSite(
            self.app, 'ploneFoo', title='Foo', setup_content=False)
        qi = get_installer(ploneSite, self.request)
        self.assertTrue(qi.is_product_installed('plone.app.dexterity'))

    def test_site_creation_without_content_but_with_content_types(self):
        """Test site creation without example content have content types."""
        ploneSite = addPloneSite(
            self.app, 'ploneFoo', title='Foo', setup_content=False)
        # Folder
        fti = queryUtility(IDexterityFTI, name='Folder')
        self.assertIsNotNone(fti)
