from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IImageScalesAdapter
from plone.base.interfaces import IImageScalesFieldAdapter
from plone.dexterity.fti import DexterityFTI
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedImage
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.CMFPlone.tests import dummy
from zope.component import queryMultiAdapter

import Missing
import unittest


class ImageScalesAdaptersRegisteredTest(unittest.TestCase):
    """Test portal actions control panel."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        news_id = self.portal.invokeFactory(
            "News Item",
            id="news",
            title="News",
        )

        image_id = self.portal.invokeFactory(
            "Image",
            id="image",
            title="image",
            image=NamedImage(dummy.Image(), filename="dummy.gif"),
        )

        self.image = self.portal[image_id]
        self.news = self.portal[news_id]

    def serialize(self, context, fieldname):
        for schema in iterSchemata(context):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        serializer = queryMultiAdapter(
            (field, context, self.request), IImageScalesFieldAdapter
        )
        if serializer:
            return serializer()
        return None

    def test_field_adapter_do_not_return_scales_for_fields_without_adapter(self):
        res = self.serialize(self.image, "title")
        self.assertEqual(res, None)

    def test_field_adapter_return_scales_for_fields_with_adapter(self):
        res = self.serialize(self.image, "image")
        self.assertNotEqual(res, None)
        self.assertEqual(len(res), 1)
        scales = res[0]
        self.assertEqual(scales["content-type"], "image/gif")
        self.assertEqual(scales["filename"], "dummy.gif")
        self.assertIn("scales", scales)
        scales = scales["scales"]
        self.assertIn("listing", scales)
        listing_scale = scales["listing"]
        self.assertIn("download", listing_scale)

    def test_field_adapter_do_not_return_scales_for_empty_fields_with_adapter(self):
        res = self.serialize(self.news, "image")
        self.assertEqual(res, None)

    def test_field_adapter_does_not_return_larger_scales(self):
        # Add an image of 900 by 900 pixels.
        image_id = self.portal.invokeFactory(
            "Image",
            id="jpeg",
            title="jpeg image",
            image=NamedImage(dummy.JpegImage(), filename="900.jpeg"),
        )
        image = self.portal[image_id]
        res = self.serialize(image, "image")
        self.assertNotEqual(res, None)
        self.assertEqual(len(res), 1)
        scales = res[0]
        self.assertEqual(scales["content-type"], "image/jpeg")
        self.assertIn("scales", scales)
        self.assertEqual(scales["filename"], "900.jpeg")
        self.assertEqual(scales["width"], 900)
        self.assertEqual(scales["height"], 900)
        download = scales["download"]
        self.assertTrue(download.startswith("@@images/image-900-"))
        self.assertTrue(download.endswith(".jpeg"))
        scales = scales["scales"]
        # larger and huge should not be in here: these scales would return the same
        # content as the original.
        self.assertEqual(
            ["icon", "large", "listing", "mini", "preview", "teaser", "thumb", "tile"],
            sorted(scales.keys()),
        )
        preview = scales["preview"]
        self.assertEqual(preview["width"], 400)
        self.assertEqual(preview["height"], 400)
        self.assertTrue(preview["download"].startswith("@@images/image-400-"))

    def test_content_adapter_return_proper_scales(self):
        res = queryMultiAdapter((self.image, self.request), IImageScalesAdapter)()
        self.assertNotEqual(res, None)
        self.assertEqual(list(res.keys()), ["image"])
        self.assertEqual(len(res["image"]), 1)
        scales = res["image"][0]
        self.assertEqual(scales["content-type"], "image/gif")
        self.assertIn("scales", scales)

    def test_content_adapter_do_not_return_scales_if_empty_fields(self):
        res = queryMultiAdapter((self.news, self.request), IImageScalesAdapter)()
        self.assertEqual(res, {})

    def test_metadata_populated_with_scales(self):
        catalog = self.portal.portal_catalog
        news_brain = catalog(UID=self.news.UID())[0]
        image_brain = catalog(UID=self.image.UID())[0]

        self.assertEqual(news_brain.image_scales, Missing.Value)
        self.assertEqual(list(image_brain.image_scales.keys()), ["image"])
        self.assertEqual(len(image_brain.image_scales["image"]), 1)
        self.assertEqual(
            image_brain.image_scales["image"][0]["content-type"], "image/gif"
        )
        self.assertIn("scales", image_brain.image_scales["image"][0])

    def test_multiple_image_fields(self):
        # Note: since there are basically three ways to set fields on an FTI, we use
        # one, and make the others explicitly None, otherwise no fields may be found.
        fti = DexterityFTI(
            "multi",
            model_file="Products.CMFPlone.image_scales.tests:images.xml",
            model_source=None,
            schema=None,
        )
        self.portal.portal_types._setObject("multi", fti)
        content_id = self.portal.invokeFactory(
            "multi",
            id="multi",
            title="Multi",
            image1=NamedImage(dummy.Image()),
            image2=NamedImage(dummy.Image()),
        )
        multi = self.portal[content_id]
        catalog = self.portal.portal_catalog
        brain = catalog(UID=multi.UID())[0]
        self.assertEqual(sorted(list(brain.image_scales.keys())), ["image1", "image2"])
