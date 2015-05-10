from Products.CMFPlone.resources.exportimport.resourceregistry import \
    ResourceRegistryNodeAdapter
from Products.CMFPlone.resources.exportimport.resourceregistry import \
    importResRegistry
from Products.ResourceRegistries.interfaces import ICSSRegistry

_FILENAME = 'cssregistry.xml'
_REG_ID = 'portal_css'
_REG_TITLE = 'Stylesheet registry'


def importCSSRegistry(context):
    """
    Import CSS registry.
    """
    return importResRegistry(context, _REG_ID, _REG_TITLE, _FILENAME)


class CSSRegistryNodeAdapter(ResourceRegistryNodeAdapter):

    """
    Node im- and exporter for CSSRegistry.
    """

    __used_for__ = ICSSRegistry
    registry_id = _REG_ID
    resource_type = 'stylesheet'
    register_method = 'registerStylesheet'
    update_method = 'updateStylesheet'
