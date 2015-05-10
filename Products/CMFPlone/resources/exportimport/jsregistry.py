from Products.ResourceRegistries.interfaces import IJSRegistry
from resourceregistry import ResourceRegistryNodeAdapter
from resourceregistry import importResRegistry

_FILENAME = 'jsregistry.xml'
_REG_ID = 'portal_javascripts'
_REG_TITLE = 'Javascript registry'


def importJSRegistry(context):
    """Import javascript registry.
    """
    return importResRegistry(context, _REG_ID, _REG_TITLE, _FILENAME)


class JSRegistryNodeAdapter(ResourceRegistryNodeAdapter):
    """Node im- and exporter for JSRegistry.
    """

    __used_for__ = IJSRegistry
    registry_id = _REG_ID
    resource_type = 'javascript'
    register_method = 'registerScript'
    update_method = 'updateScript'

    # We already have jQuery, blacklist legacy installs of plone.app.jquery js
    resource_blacklist = set((
        "++resource++plone.app.jquery.js",
    ))
