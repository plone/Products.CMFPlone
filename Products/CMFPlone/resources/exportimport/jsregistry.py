from Products.ResourceRegistries.interfaces import IJSRegistry

from resourceregistry import ResourceRegistryNodeAdapter, \
     importResRegistry, exportResRegistry

_FILENAME = 'jsregistry.xml'
_REG_ID = 'portal_javascripts'
_REG_TITLE = 'Javascript registry'

def importJSRegistry(context):
    """
    Import javascript registry.
    """
    return importResRegistry(context, _REG_ID, _REG_TITLE, _FILENAME)

def exportJSRegistry(context):
    """
    Export javascript registry.
    """
    return exportResRegistry(context, _REG_ID, _REG_TITLE, _FILENAME)


class JSRegistryNodeAdapter(ResourceRegistryNodeAdapter):
    """
    Node im- and exporter for JSRegistry.
    """

    __used_for__ = IJSRegistry
    registry_id = _REG_ID
    resource_type = 'javascript'
    register_method = 'registerScript'
    update_method = 'updateScript'
