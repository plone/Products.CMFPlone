from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.resources.interfaces import ICSSManualResource
from Products.CMFPlone.resources.interfaces import IJSManualResource
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

    importer.registry = getToolByName(site, 'portal_registry')
    importer.body = body
    logger.info("%s imported." % reg_title)


class ResourceRegistryNodeAdapter(XMLAdapterBase):

    def _importNode(self, node):
        """
        Import the object from the DOM node.
        """

        for child in node.childNodes:
            if child.nodeName != self.resource_type:
                continue

            data = {}
            add = True
            position = None
            for key, value in child.attributes.items():
                key = str(key)
                if key == 'update':
                    continue
                if key == 'remove':
                    add = False
                    continue
                if key in ('position-before', 'insert-before'):
                    position = ('before', queryUtility(IIDNormalizer).normalize(str(value)))
                    continue
                if key in ('position-after', 'insert-after'):
                    position = ('after', queryUtility(IIDNormalizer).normalize(str(value)))
                    continue
                if key in ('position-top', 'insert-top'):
                    position = ('*',)
                    continue
                if key in ('position-bottom', 'insert-bottom'):
                    position = ('',)
                    continue
                if key == 'id':
                    res_id = queryUtility(IIDNormalizer).normalize(str(value))
                    data['url'] = str(value)
                elif value.lower() == 'false':
                    data[key] = False
                elif value.lower() == 'true':
                    data[key] = True
                else:
                    try:
                        data[key] = int(value)
                    except ValueError:
                        data[key] = str(value)

            if add:
                if self.resource_type == 'javascript':
                    collection = self.registry.collectionOfInterface(
                                     IJSManualResource,
                                     prefix="Products.CMFPlone.manualjs")
                elif self.resource_type == 'stylesheet':
                    collection = self.registry.collectionOfInterface(
                                     ICSSManualResource,
                                     prefix="Products.CMFPlone.manualcss")
                proxy = collection.setdefault(res_id)
                proxy.url = data['url']
                if 'conditionalcomment' in data:
                    proxy.conditionalcomment = data['conditionalcomment']
                if 'expression' in data:
                    proxy.expression = data['expression']
                if 'enabled' in data:
                    proxy.enabled = data['enabled']
                if position is not None:
                    if position[0] == '*' or position[0] == '':
                        proxy.depends = position[0]
                    elif position[0] == 'after':
                        if position[1] in collection:
                            collection[position[1]].depends = res_id
                    elif position[0] == 'before':
                        proxy.depends = queryUtility(IIDNormalizer).normalize(str(position[1]))
