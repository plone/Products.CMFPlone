from zope.component import queryMultiAdapter

from Products.CMFCore.utils import getToolByName

from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import XMLAdapterBase


def importResRegistry(context, reg_id, reg_title, filename):
    """
    Import resource registry.
    """
    site = context.getSite()
    logger = context.getLogger('resourceregistry')

    body = context.readDataFile(filename)
    if body is None:
        return

    res_reg = getToolByName(site, reg_id)

    importer = queryMultiAdapter((res_reg, context), IBody)
    if importer is None:
        logger.warning("%s: Import adapter missing." % reg_title)
        return

    importer.body = body
    logger.info("%s imported." % reg_title)

def exportResRegistry(context, reg_id, reg_title, filename):
    """
    Export resource registry.
    """
    site = context.getSite()
    logger = context.getLogger('resourceregistry')
    res_reg = getToolByName(site, reg_id, None)
    if res_reg is None:
        return

    exporter = queryMultiAdapter((res_reg, context), IBody)
    if exporter is None:
        logger.warning("%s: Export adapter missing." % reg_title)
        return

    context.writeDataFile(filename, exporter.body, exporter.mime_type)
    logger.info("%s exported" % reg_title)


class ResourceRegistryNodeAdapter(XMLAdapterBase):

    unregister_method = 'unregisterResource'

    def _exportNode(self):
        """
        Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        child = self._extractResourceInfo()
        node.appendChild(child)
        return node

    def _importNode(self, node):
        """
        Import the object from the DOM node.
        """
        registry = getToolByName(self.context, self.registry_id)
        if self.environ.shouldPurge():
            registry.clearResources()
        self._initResources(node)

    def _extractResourceInfo(self):
        """
        Extract the information for each of the registered resources.
        """
        fragment = self._doc.createDocumentFragment()
        registry = getToolByName(self.context, self.registry_id)
        resources = registry.getResources()
        old_child_id = None

        for resource in resources:
            data = resource._data.copy()
            if 'cooked_expression' in data:
                del data['cooked_expression']
            child = self._doc.createElement(self.resource_type)
            attributes = data.items()

            if old_child_id is not None:
                attributes.append(('insert-after', old_child_id))

            for key, value in attributes:
                if isinstance(value, bool) or isinstance(value, int):
                    value = str(value)
                child.setAttribute(key, value)
            fragment.appendChild(child)

            old_child_id = data['id']

        return fragment

    def _initResources(self, node):
        """
        Initialize the registered resources based on the contents of
        the provided DOM node.
        """
        registry = getToolByName(self.context, self.registry_id)
        reg_method = getattr(registry, self.register_method)
        unreg_method = getattr(registry, self.unregister_method)
        update_method = getattr(registry, self.update_method)
        if getattr(node.attributes.get('purge'), 'value', '') == 'true':
            registry.clearResources()
        for child in node.childNodes:
            if child.nodeName != self.resource_type:
                continue

            data = {}
            method = reg_method
            position = None
            for key, value in child.attributes.items():
                key = str(key)
                if key == 'update':
                    method = update_method
                    continue
                if key == 'remove':
                    method = unreg_method
                    continue
                if key in ('position-before', 'insert-before'):
                    position = ('Before', value)
                    continue
                if key in ('position-after', 'insert-after'):
                    position = ('After', value)
                    continue
                if key in ('position-top', 'insert-top'):
                    position = ('ToTop',)
                    continue
                if key in ('position-bottom', 'insert-bottom'):
                    position = ('ToBottom',)
                    continue
                if key == 'id':
                    res_id = str(value)
                elif value.lower() == 'false':
                    data[key] = False
                elif value.lower() == 'true':
                    data[key] = True
                else:
                    try:
                        data[key] = int(value)
                    except ValueError:
                        data[key] = str(value)

            # unreg_method doesn't expect any keyword arguments
            # and has to be called separately (this feels dirty..)
            if method == unreg_method:
                method(res_id)
            elif method == reg_method:
                try:
                    data['skipCooking'] = True
                    method(res_id, **data)
                    del data['skipCooking']
                except ValueError:
                    # this feels a bit dirty too, but we always want to update
                    # if the resource already exists (in which case 'ValueError:
                    # Duplicate id ...' is raised.
                    method=update_method
                    del data['skipCooking']
            if method == update_method:
                method(res_id, **data)
            if position is not None:
                moveMethod = getattr(registry, 'moveResource' + position[0])
                moveMethod(res_id, *position[1:])

        registry.cookResources()
