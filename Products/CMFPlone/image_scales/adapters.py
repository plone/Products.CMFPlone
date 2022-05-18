from zope.globalrequest import getRequest
from plone.namedfile.interfaces import INamedImageField
from Acquisition import aq_inner
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.CMFPlone.image_scales.interfaces import IImageScalesAdapter
from Products.CMFPlone.image_scales.interfaces import IImageScalesFieldAdapter
from Products.CMFPlone.interfaces import IImagingSchema


@implementer(IImageScalesAdapter)
@adapter(IDexterityContent, Interface)
class ImageScales:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        obj = aq_inner(self.context)
        res = {}

        for schema in iterSchemata(self.context):
            for name, field in getFields(schema).items():
                # serialize the field
                serializer = queryMultiAdapter(
                    (field, obj, self.request), IImageScalesFieldAdapter
                )
                if serializer:
                    scales = serializer()
                    if scales:
                        res[name] = scales
        return res


@implementer(IImageScalesFieldAdapter)
@adapter(INamedImageField, IDexterityContent, Interface)
class ImageFieldScales:
    def __init__(self, field, context, request):
        self.context = context
        self.request = request
        self.field = field

    def __call__(self):
        image = self.field.get(self.context)
        if not image:
            return

        width, height = image.getImageSize()

        url = self.get_original_image_url(self.field.__name__, width, height)

        scales = self.get_scales(self.field, width, height)
        return [
            {
                "filename": image.filename,
                "content-type": image.contentType,
                "size": image.getSize(),
                "download": url,
                "width": width,
                "height": height,
                "scales": scales,
            }
        ]

    def get_scales(self, field, width, height):
        """Get a dictionary of available scales for a particular image field,
        with the actual dimensions (aspect ratio of the original image).
        """
        scales = {}
        request = getRequest()
        images_view = getMultiAdapter((self.context, request), name="images")

        for name, actual_width, actual_height in self.get_scale_infos():
            # Get the scale info without actually generating the scale,
            # nor any old-style HiDPI scales.
            scale = images_view.scale(
                field.__name__,
                width=actual_width,
                height=actual_height,
                pre=True,
                include_srcset=False,
            )
            if scale is None:
                # If we cannot get a scale, it is probably a corrupt image.
                continue

            url = self.get_scale_url(scale=scale)
            actual_width = scale.width
            actual_height = scale.height

            scales[name] = {
                "download": url,
                "width": actual_width,
                "height": actual_height,
            }

        return scales

    def get_original_image_url(self, fieldname, width, height):
        request = getRequest()
        images_view = getMultiAdapter((self.context, request), name="images")
        scale = images_view.scale(
            fieldname, width=width, height=height, direction="thumbnail"
        )
        if scale:
            return self.get_scale_url(scale=scale)
        # Corrupt images may not have a scale.

    def get_actual_scale(self, dimensions, bbox):
        """Given dimensions of an original image, and a bounding box of a scale,
        calculates what actual dimensions that scaled image would have,
        maintaining aspect ratio.

        This is supposed to emulate / predict the behavior of Plone's
        ImageScaling implementations.
        """
        width, height = dimensions
        max_width, max_height = bbox
        resize_ratio = min(max_width / width, max_height / height)

        # Plone doesn't upscale images for the default named scales - limit
        # to actual image dimensions
        resize_ratio = min(resize_ratio, 1.0)

        scaled_dimensions = int(width * resize_ratio), int(height * resize_ratio)

        # Don't produce zero pixel lengths
        scaled_dimensions = tuple(max(1, dim) for dim in scaled_dimensions)
        return scaled_dimensions

    def get_scale_infos(self):
        """Returns a list of (name, width, height) 3-tuples of the
        available image scales.
        """

        registry = getUtility(IRegistry)

        imaging_settings = registry.forInterface(IImagingSchema, prefix="plone")
        allowed_sizes = imaging_settings.allowed_sizes

        def split_scale_info(allowed_size):
            name, dims = allowed_size.split(" ")
            width, height = list(map(int, dims.split(":")))
            return name, width, height

        return [split_scale_info(size) for size in allowed_sizes]

    def get_scale_url(self, scale):
        return scale.url
