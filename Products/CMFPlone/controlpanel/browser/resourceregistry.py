from Products.Five import BrowserView
import json
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.resources.interfaces import (
    IBundleRegistry, IResourceRegistry
)
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.resources.interfaces import (
    OVERRIDE_RESOURCE_DIRECTORY_NAME)
from StringIO import StringIO
from zExceptions import NotFound


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
            setattr(record, name, val)


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
        req = self.request
        resource_path = req.form.get('filepath').split('++plone++')[-1]
        resource_name, resource_filepath = resource_path.split('/', 1)

        persistent_directory = getUtility(IResourceDirectory, name="persistent")  # noqa
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)  # noqa
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        if resource_name not in container:
            container.makeDirectory(resource_name)
        folder = container[resource_name]
        fi = StringIO(req.form['data'])
        folder.writeFile(resource_filepath, fi)
        return json.dumps({
            'success': True
        })

    def get_parent(self, item):
        path = '/'.join(item.getPhysicalPath()[:-1])
        return self.context.restrictedTraverse(path)

    def list_dir(self, container):
        if hasattr(container, 'listDirectory'):
            return container.listDirectory()
        else:
            return container.objectIds()

    def delete_file(self):
        req = self.request
        resource_path = req.form.get('filepath').split('++plone++')[-1]
        resource_name, resource_filepath = resource_path.split('/', 1)

        persistent_directory = getUtility(IResourceDirectory, name="persistent")  # noqa
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)  # noqa
        container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
        if resource_name not in container:
            return
        folder = container[resource_name]
        try:
            fi = folder[resource_filepath]
        except NotFound:
            return
        parent = self.get_parent(fi)
        del parent[fi.getId()]

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