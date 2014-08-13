from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.resources.interfaces import IResourceRegistry
from Products.CMFPlone.resources.interfaces import IBundleRegistry
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

        resources = self.registry.collectionOfInterface(
                         IResourceRegistry,
                         prefix="Products.CMFPlone.resources")

        bundles = self.registry.collectionOfInterface(
                         IBundleRegistry,
                         prefix="Products.CMFPlone.bundles")
        if 'plone-legacy' in bundles:
            legacy = bundles['plone-legacy']
        else:
            legacy = bundles.setdefault('plone-legacy')
            legacy.resources = []
            legacy.enabled = True

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
                proxy = resources.setdefault(res_id)
                if self.resource_type == 'javascript':
                    proxy.js = data['url']
                elif self.resource_type == 'stylesheet':
                    proxy.css = [data['url']]
                if 'enabled' in data and not data['enabled']:
                    continue
                if position is None:
                    position = ('',)
                if position[0] == '*':
                    legacy.resources.insert(0, res_id)
                elif position[0] == '':
                    legacy.resources.append(res_id)
                elif position[0] == 'after':
                    if position[1] in legacy.resources:
                        legacy.resources.insert(
                            legacy.resources.index(position[1]) + 1,
                            res_id)
                    else:
                        legacy.resources.append(res_id)
                elif position[0] == 'before':
                    if position[1] in legacy.resources:
                        legacy.resources.insert(
                            legacy.resources.index(position[1]) + 1,
                            res_id)
                    else:
                        legacy.resources.append(res_id)
