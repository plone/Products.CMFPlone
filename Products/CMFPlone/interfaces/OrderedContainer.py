import zope.deferredimport

zope.deferredimport.deprecated(
    "Please use the canonical interface from OFS. "
    "This alias will be removed in Plone 5.0",
    IOrderedContainer = 'OFS.interfaces:IOrderedContainer',
    )
