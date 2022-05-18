from persistent.dict import PersistentDict
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from Products.CMFPlone.image_scales.interfaces import IImageScalesAdapter
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest


@indexer(IDexterityContent)
def image_scales(obj):
    """
    Indexer used to store in metadata the image scales of the object.
    """
    adapter = queryMultiAdapter((obj, getRequest()), IImageScalesAdapter)
    if not adapter:
        return
    scales = adapter()
    if not scales:
        return
    return PersistentDict(scales)
