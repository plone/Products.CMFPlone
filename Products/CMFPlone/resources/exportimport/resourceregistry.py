from datetime import datetime

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from Products.GenericSetup.interfaces import IBody
from Products.GenericSetup.utils import XMLAdapterBase
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.interfaces import ComponentLookupError


def importResRegistry(context, reg_id, reg_title, filename):
    """Import resource registry.
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
    try:
        importer.registry = getToolByName(site, 'portal_registry')
    except AttributeError:
        # Upgrade 3.x no registry there
        importer.registry = None
    importer.body = body
    logger.info("%s imported." % reg_title)


class ResourceRegistryNodeAdapter(XMLAdapterBase):

    resource_blacklist = set()

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.registry is None:
            # Upgrade 3.x no registry there
            return
        resources = self.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources", check=False)

        bundles = self.registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles", check=False)
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
            remove = False
            position = res_id = None
            for key, value in child.attributes.items():
                key = str(key)
                if key == 'update':
                    continue
                if key == 'remove' and value in (True, 'true', 'True'):
                    add = False
                    remove = True
                    continue
                if key in ('position-before', 'insert-before'):
                    position = ('before', queryUtility(
                        IIDNormalizer).normalize(str(value)))
                    continue
                if key in ('position-after', 'insert-after'):
                    position = ('after', queryUtility(
                        IIDNormalizer).normalize(str(value)))
                    continue
                if key in ('position-top', 'insert-top'):
                    position = ('*',)
                    continue
                if key in ('position-bottom', 'insert-bottom'):
                    position = ('',)
                    continue
                if key == 'id':
                    if value in self.resource_blacklist:
                        add = False
                        data.clear()
                        break
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
                    # if we are disabling it, we need to remove from legacy resources
                    if res_id in legacy.resources:
                        legacy.resources.remove(res_id)
                    continue
                if res_id in legacy.resources:
                    # remove here so we can possible re-insert into whatever
                    # position is preferred below and then we do not
                    # re-add same resource multiple times
                    legacy.resources.remove(res_id)
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

            if remove:
                if res_id in legacy.resources:
                    legacy.resources.remove(res_id)
                if res_id in resources:
                    del resources[res_id]

            # make sure to trigger committing to db
            # not sure this is necessary...
            legacy.resources = legacy.resources

        if 'plone.resources.last_legacy_import' in self.registry.records:  # noqa
            self.registry.records[
                'plone.resources.last_legacy_import'
            ].value = datetime.now()
            try:
                cookWhenChangingSettings(self.context, legacy)
            except (AssertionError, ComponentLookupError):
                # zope.globalrequest and the site might not be setup, don't error out
                pass