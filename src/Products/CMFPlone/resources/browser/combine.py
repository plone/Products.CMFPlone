import zope.deferredimport

zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Import from Products.CMFPlone.resources.utils instead",
    PRODUCTION_RESOURCE_DIRECTORY="Products.CMFPlone:resources.utils.PRODUCTION_RESOURCE_DIRECTORY",
    get_override_directory="Products.CMFPlone:resources.utils.get_override_directory",
)
