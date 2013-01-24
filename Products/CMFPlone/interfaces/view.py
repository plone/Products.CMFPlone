import zope.deferredimport

zope.deferredimport.deprecated(
    "It has been moved to Products.CMFDynamicViewFTI.interfaces. "
    "This alias will be removed in Plone 5.0",
    IBrowserDefault='Products.CMFDynamicViewFTI.interfaces:IBrowserDefault',
    )

zope.deferredimport.deprecated(
    "It has been moved to Products.CMFDynamicViewFTI.interfaces. "
    "This alias will be removed in Plone 5.0",
    IDynamicViewTypeInformation='Products.CMFDynamicViewFTI.interfaces:IDynamicViewTypeInformation',
    )

zope.deferredimport.deprecated(
    "It has been moved to Products.CMFDynamicViewFTI.interfaces. "
    "This alias will be removed in Plone 5.0",
    ISelectableBrowserDefault='Products.CMFDynamicViewFTI.interfaces:ISelectableBrowserDefault',
    )
