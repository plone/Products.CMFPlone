# -*- coding: utf-8 -*-
# From Products.PloneHotfix20160419
# Plus extras for properties.
from OFS.PropertyManager import PropertyManager
from OFS.ZDOM import Document
from OFS.ZDOM import Node
from Products.CMFPlone.Portal import PloneSite


try:
    from plone.dexterity.content import Item
    from plone.dexterity.content import Container
except ImportError:
    class Item(object):
        pass

    class Container(object):
        pass

try:
    from Products.ATContentTypes.content.base import ATCTContent
    from Products.ATContentTypes.content.base import ATCTBTreeFolder
except ImportError:

    class ATCTContent(object):
        pass

    class ATCTBTreeFolder(object):
        pass


klasses = (
    Node,
    Document,
    PloneSite,
    Item,
    Container,
    ATCTContent,
    ATCTBTreeFolder
)
methods = (
    'EffectiveDate',
    'ExpirationDate',
    'getAttributes',
    'getChildNodes',
    'getFirstChild',
    'getLastChild',
    'getLayout',
    'getNextSibling',
    'getNodeName',
    'getNodeType',
    'getNodeValue',
    'getOwnerDocument',
    'getParentNode',
    'getPhysicalPath',
    'getPreviousSibling',
    'getTagName',
    'hasChildNodes',
    'Type'
)

for klass in klasses:
    for method_name in methods:
        method = getattr(klass, method_name, None)
        if (method is not None and hasattr(method, 'im_func') and
                hasattr(method.im_func, '__doc__')):
            del method.im_func.__doc__

property_methods = (
    'getProperty',
    'propertyValues',
    'propertyItems',
    'propertyMap',
    'hasProperty',
    'getPropertyType',
    'propertyIds',
    'propertyLabel',
    'propertyDescription'
)

for method_name in property_methods:
    method = getattr(PropertyManager, method_name, None)
    if (method is not None and hasattr(method, 'im_func') and
            hasattr(method.im_func, '__doc__')):
        del method.im_func.__doc__
