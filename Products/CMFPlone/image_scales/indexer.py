from persistent.dict import PersistentDict
from plone.base.interfaces import IImageScalesAdapter
from plone.dexterity.interfaces import IDexterityContent
from plone.indexer.decorator import indexer
from zope.component import queryMultiAdapter
from zope.globalrequest import getRequest


@indexer(IDexterityContent)
def image_scales(obj):
    """
    Indexer used to store in metadata the image scales of the object.
    """
    adapter = queryMultiAdapter((obj, getRequest()), IImageScalesAdapter)
    if not adapter:
        # Raising an AttributeError does the right thing,
        # making sure nothing is saved in the catalog.
        raise AttributeError
    scales = adapter()
    if not scales:
        raise AttributeError
    return PersistentDict(scales)
