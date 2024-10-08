from importlib.metadata import distribution
from importlib.metadata import PackageNotFoundError
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.CMFPlone.testing import (
    PRODUCTS_CMFPLONE_DISTRIBUTIONS_INTEGRATION_TESTING,
)
from Products.CMFPlone.utils import get_installer
from zope.component import getUtility
from zope.component import queryUtility

import unittest


try:
    distribution("plone.distribution")
    HAS_DISTRIBUTION = True
except PackageNotFoundError:
    HAS_DISTRIBUTION = False


class TestFactoryPloneSite(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.request = self.layer["request"]

    def testPlonesiteWithUnicodeTitle(self):
        TITLE = "Ploné"
        ploneSite = addPloneSite(self.app, "ploneFoo", title=TITLE)
        ploneSiteTitleProperty = ploneSite.getProperty("title")
        # CMF stores title as string only so Plone should keep the same track
        self.assertTrue(isinstance(ploneSiteTitleProperty, str))
        self.assertEqual(ploneSiteTitleProperty, TITLE)
        ploneSiteTitle = ploneSite.Title()
        self.assertTrue(isinstance(ploneSiteTitle, str))
        self.assertEqual(ploneSiteTitle, TITLE)

    def testPlonesiteWithoutUnicodeTitle(self):
        TITLE = "Plone"
        ploneSite = addPloneSite(self.app, "ploneFoo", title=TITLE)
        ploneSiteTitleProperty = ploneSite.getProperty("title")
        # CMF stores title as string only so Plone should keep the same track
        self.assertTrue(isinstance(ploneSiteTitleProperty, str))
        self.assertEqual(ploneSiteTitleProperty, TITLE)
        ploneSiteTitle = ploneSite.Title()
        self.assertTrue(isinstance(ploneSiteTitle, str))
        self.assertEqual(ploneSiteTitle, TITLE)

    def test_site_creation_has_no_dexterity(self):
        """Test site creation does not even have dexterity installed.

        If you want it, you need to pass more extension_ids,
        like the plone-addsite view does.
        """
        ploneSite = addPloneSite(self.app, "ploneFoo", title="Foo")
        qi = get_installer(ploneSite, self.request)
        self.assertFalse(qi.is_product_installed("plone.app.dexterity"))

    def test_site_creation_has_no_content_types(self):
        """Test site creation has no content types.

        If you want them, you need to pass more extension_ids,
        like the plone-addsite view does.
        """
        addPloneSite(self.app, "ploneFoo", title="Foo")
        # Folder
        fti = queryUtility(IDexterityFTI, name="Folder")
        self.assertIsNone(fti)
        # For good measure we check that there is at least on FTI.
        fti = queryUtility(IDexterityFTI, name="Plone Site")
        self.assertIsNotNone(fti)

    def test_site_creation_title_is_set_in_registry(self):
        """Plone site title should be stored in registry"""
        ploneSite = addPloneSite(self.app, "ploneFoo", title="Foo")
        registry = getUtility(IRegistry, context=ploneSite)
        self.assertEqual(registry["plone.site_title"], "Foo")


class TestFactoryDistributionPloneSite(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_DISTRIBUTIONS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.request = self.layer["request"]

    @unittest.skipIf(
        not HAS_DISTRIBUTION,
        "Passing a distribution_name needs plone.distribution.",
    )
    def test_site_creation_distribution(self):
        """Create a Plone Site using a distribution"""
        ploneSite = addPloneSite(
            self.app,
            "ploneFoo",
            title="Foo",
            distribution_name="testdistro",
            default_language="nl",
        )
        self.assertEqual(ploneSite.getId(), "ploneFoo")
        self.assertEqual(ploneSite.title, "Foo")
        self.assertEqual(ploneSite.Language(), "nl")
