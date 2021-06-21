# -*- coding: utf-8 -*-
# From Products.PloneHotfix20160419
# Plus extras for properties.
# Plus Products.PloneHotfix20210518.
from OFS.PropertyManager import PropertyManager
#from OFS.ZDOM import Document
#from OFS.ZDOM import Node
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


def delete_method_docstring(klass, method_name):
    # Delete the docstring from the class method.
    # Objects must have a docstring to be published.
    # So this avoids them getting published.
    method = getattr(klass, method_name, None)
    if method is None:
        return
    if hasattr(method, "im_func"):
        # Only Python 2 has im_func.
        # Python 3 has __func__, but only on methods of instances, not classes.
        if hasattr(method.im_func, "__doc__"):
            del method.im_func.__doc__
    else:
        # This would fail on Python 2 with an AttributeError:
        # "attribute '__doc__' of 'instancemethod' objects is not writable"
        if hasattr(method, "__doc__"):
            del method.__doc__


klasses = (
#    Node,
#    Document,
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
        delete_method_docstring(klass, method_name)

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
    delete_method_docstring(PropertyManager, method_name)
