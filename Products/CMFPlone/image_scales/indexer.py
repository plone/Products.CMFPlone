from Acquisition import aq_base
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from plone.volto.behaviors.preview import IPreview
from persistent.dict import PersistentDict
from zope.globalrequest import getRequest
from plone.namedfile.interfaces import INamedImageField
from Acquisition import aq_inner
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.utils import iterSchemata
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema import getFields
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.CMFPlone.image_scales.interfaces import IImageScalesAdapter


@indexer(IDexterityContent)
def image_scales(obj):
    """
    Indexer used to store in metadata the image scales of the object.
    """
    base_obj = aq_base(obj)
    request = getRequest()
    data = PersistentDict()
    adapter = queryMultiAdapter((obj, request), IImageScalesAdapter)
    scales = adapter()
    return PersistentDict(scales)
