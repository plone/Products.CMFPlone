from Products.Five import BrowserView
import json
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import (
    IBundleRegistry, IResourceRegistry
)


def recordsToDict(record):
    data = {}
    for name in record.__schema__.names():
        data[name] = getattr(record, name)
    return data


def updateRecordFromDict(record, data):
    for name in record.__schema__.names():
        if name in data:
            # almost all string data needs to be str, not unicode
            val = data[name]
            if isinstance(val, unicode):
                val = val.encode('utf-8')
            if isinstance(val, list):
                newval = []
                for item in val:
                    if isinstance(item, unicode):
                        item = item.encode('utf-8')
                    newval.append(item)
                val = newval
            try:
                setattr(record, name, val)
            except Exception, ex:
                import pdb; pdb.set_trace()
                raise


class ResourceRegistryControlPanelView(BrowserView):

    def __call__(self):
        req = self.request
        if req.REQUEST_METHOD == 'POST':
            action = req.get('action')
            if action == 'save-registry':
                return self.save_registry()
            elif action == 'save-file':
                return self.save_file()
            elif action == 'delete-file':
                return self.delete_file()
            elif action == 'build':
                return self.build()
        else:
            return self.index()

    def save_registry(self):
        req = self.request
        registry = getUtility(IRegistry)

        resourcesData = json.loads(req.get('resources'))
        resources = registry.collectionOfInterface(
            IResourceRegistry, prefix="Products.CMFPlone.resources")
        for key, data in resourcesData.items():
            if key not in resources:
                record = resources.add(key)
            else:
                record = resources[key]
            updateRecordFromDict(record, data)
        # remove missing ones
        for key in set(resources.keys()) - set(resourcesData.keys()):
            del resources[key]

        bundlesData = json.loads(req.get('bundles'))
        bundles = registry.collectionOfInterface(
            IBundleRegistry, prefix="Products.CMFPlone.bundles")
        for key, data in bundlesData.items():
            if key not in bundles:
                record = bundles.add(key)
            else:
                record = bundles[key]
            updateRecordFromDict(record, data)
        # remove missing ones
        for key in set(bundles.keys()) - set(bundlesData.keys()):
            del bundles[key]

        return json.dumps({
            'success': True
        })

    def save_file(self):
        pass

    def delete_file(self):
        pass

    def build(self):
        pass

    def config(self):
        registry = getUtility(IRegistry)
        base_url = self.context.absolute_url()
        data = {
            'resources': {},
            'bundles': {},
            'baseUrl': base_url,
            'manageUrl': '%s/@@resourceregistry-controlpanel' % base_url
        }
        resources = registry.collectionOfInterface(
            IResourceRegistry, prefix="Products.CMFPlone.resources")
        bundles = registry.collectionOfInterface(
            IBundleRegistry, prefix="Products.CMFPlone.bundles")
        for key, resource in resources.items():
            data['resources'][key] = recordsToDict(resource)
        for key, bundle in bundles.items():
            data['bundles'][key] = recordsToDict(bundle)
        return json.dumps(data)