from Acquisition import aq_inner
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.namedfile.interfaces import INamedImageField
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.image_scales.interfaces import IImageScalesAdapter
from Products.CMFPlone.image_scales.interfaces import IImageScalesFieldAdapter
from Products.CMFPlone.interfaces import IImagingSchema
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields


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


def _split_scale_info(allowed_size):
    name, dims = allowed_size.split(" ")
    width, height = list(map(int, dims.split(":")))
    return name, width, height


def _get_scale_infos():
    """Returns list of (name, width, height) of the available image scales."""
    registry = getUtility(IRegistry)
    imaging_settings = registry.forInterface(IImagingSchema, prefix="plone")
    allowed_sizes = imaging_settings.allowed_sizes
    return [_split_scale_info(size) for size in allowed_sizes]


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

        # Get the @@images view once and store it, so all methods can use it.
        self.images_view = getMultiAdapter((self.context, self.request), name="images")

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

        for name, actual_width, actual_height in _get_scale_infos():
            if actual_width > width:
                # The width of the scale is larger than the original width.
                # Scaling would simply return the original (or perhaps a copy
                # with the same size).  We do not need this scale.
                continue

            # Get the scale info without actually generating the scale,
            # nor any old-style HiDPI scales.
            scale = self.images_view.scale(
                field.__name__,
                width=actual_width,
                height=actual_height,
                pre=True,
                include_srcset=False,
            )
            if scale is None:
                # If we cannot get a scale, it is probably a corrupt image.
                continue

            url = scale.url
            actual_width = scale.width
            actual_height = scale.height

            scales[name] = {
                "download": url,
                "width": actual_width,
                "height": actual_height,
            }

        return scales

    def get_original_image_url(self, fieldname, width, height):
        scale = self.images_view.scale(
            fieldname, width=width, height=height, direction="thumbnail"
        )
        # Corrupt images may not have a scale.
        return scale.url if scale else None
