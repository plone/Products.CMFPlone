from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.CMFPlone.tests import dummy
from zope.component import queryMultiAdapter
from plone.namedfile.file import NamedImage
from plone.dexterity.utils import iterSchemata
from Products.CMFPlone.image_scales.interfaces import IImageScalesAdapter
from Products.CMFPlone.image_scales.interfaces import IImageScalesFieldAdapter
from zope.interface.interfaces import ComponentLookupError

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
            image=NamedImage(dummy.Image()),
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
        data = self.serialize(self.image, "title")
        self.assertEqual(data, None)

    def test_field_adapter_return_scales_for_fields_with_adapter(self):
        data = self.serialize(self.image, "image")
        self.assertNotEqual(data, None)
        self.assertEqual(data["content-type"], "image/gif")
        self.assertIn("scales", data)

    def test_field_adapter_do_not_return_scales_for_empty_fields_with_adapter(self):
        data = self.serialize(self.news, "image")
        self.assertEqual(data, None)

    def test_content_adapter_return_proper_scales(self):
        data = queryMultiAdapter((self.image, self.request), IImageScalesAdapter)()
        self.assertNotEqual(data, None)
        self.assertEqual(list(data.keys()), ["image"])
        self.assertEqual(data["image"]["content-type"], "image/gif")
        self.assertIn("scales", data["image"])

    def test_content_adapter_do_not_return_scales_if_empty_fields(self):
        data = queryMultiAdapter((self.news, self.request), IImageScalesAdapter)()
        self.assertEqual(data, {})

    def test_metadata_populated_with_scales(self):
        catalog = self.portal.portal_catalog
        news_brain = catalog(UID=self.news.UID())[0]
        image_brain = catalog(UID=self.image.UID())[0]

        self.assertEqual(news_brain.image_scales, {})

        self.assertEqual(list(image_brain.image_scales.keys()), ["image"])
        self.assertEqual(image_brain.image_scales["image"]["content-type"], "image/gif")
        self.assertIn("scales", image_brain.image_scales["image"])
