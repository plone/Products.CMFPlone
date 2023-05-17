# From Products.PloneHotfix20160419
# Plus extras for properties.
# Plus Products.PloneHotfix20210518.
from OFS.PropertyManager import PropertyManager
from plone.dexterity.content import Container
from plone.dexterity.content import Item
from Products.CMFPlone.Portal import PloneSite


def delete_method_docstring(klass, method_name):
    # Delete the docstring from the class method.
    # Objects must have a docstring to be published.
    # So this avoids them getting published.
    method = getattr(klass, method_name, None)
    if method is None:
        return
    if hasattr(method, "__doc__"):
        del method.__doc__


klasses = (
    #    Node,
    #    Document,
    PloneSite,
    Item,
    Container,
)
methods = (
    "EffectiveDate",
    "ExpirationDate",
    "getAttributes",
    "getChildNodes",
    "getFirstChild",
    "getLastChild",
    "getLayout",
    "getNextSibling",
    "getNodeName",
    "getNodeType",
    "getNodeValue",
    "getOwnerDocument",
    "getParentNode",
    "getPhysicalPath",
    "getPreviousSibling",
    "getTagName",
    "hasChildNodes",
    "Type",
)

for klass in klasses:
    for method_name in methods:
        delete_method_docstring(klass, method_name)

property_methods = (
    "getProperty",
    "propertyValues",
    "propertyItems",
    "propertyMap",
    "hasProperty",
    "getPropertyType",
    "propertyIds",
    "propertyLabel",
    "propertyDescription",
)

for method_name in property_methods:
    delete_method_docstring(PropertyManager, method_name)
