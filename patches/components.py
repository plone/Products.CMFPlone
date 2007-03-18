from Acquisition import aq_base
from Products.GenericSetup.utils import _resolveDottedName


def _initUtilities(self, node):
    for child in node.childNodes:
        if child.nodeName != 'utility':
            continue

        provided = _resolveDottedName(child.getAttribute('interface'))
        name = unicode(str(child.getAttribute('name')))

        component = child.getAttribute('component')
        component = component and _resolveDottedName(component) or None

        factory = child.getAttribute('factory')
        factory = factory and _resolveDottedName(factory) or None

        obj_path = child.getAttribute('object')
        if obj_path:
            site = self.environ.getSite()
            # we support registering aq_wrapped objects only for now
            if hasattr(site, 'aq_base'):
                # filter out empty path segments
                path = [f for f in obj_path.split('/') if f]
                # support for nested folder
                obj = self._recurseFolder(site, path)
                if obj is not None:
                    self.context.registerUtility(aq_base(obj), provided, name)
            else:
                # Log an error, not aq_wrapped
                self._logger.warning("The object %s was not acquisition "
                                     "wrapped. Registering these is not "
                                     "supported right now." % obj_path)
        elif component:
            self.context.registerUtility(component, provided, name)
        else:
            self.context.registerUtility(factory(), provided, name)


# Apply temporary monkey-patch which makes sure we don't register
# Acquisition wrapped utilites, as this breaks horribly.
from Products.GenericSetup import components

components.ComponentRegistryXMLAdapter._initUtilities = _initUtilities
