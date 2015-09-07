# -*- coding:utf-8
from datetime import datetime
import json
import re
from urlparse import urlparse

from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces import IResourceRegistry
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME  # noqa
from Products.CMFPlone.resources import RESOURCE_DEVELOPMENT_MODE
from Products.CMFPlone.resources import add_bundle_on_request
from Products.CMFPlone.resources.browser.configjs import RequireJsView
from Products.CMFPlone.resources.browser.cook import cookWhenChangingSettings
from Products.statusmessages.interfaces import IStatusMessage
from plone.memoize.view import memoize
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.resource.interfaces import IResourceDirectory
import posixpath
from zExceptions import NotFound
from zope.component import getUtility


CSS_URL_REGEX = re.compile('url\(([^)]+)\)')


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            return json.JSONEncoder.default(self, obj)


def recordsToDict(record):
    data = {}
    for name in record.__schema__.names():
        data[name] = getattr(record, name)
    return data


def updateRecordFromDict(record, data):
    for name in record.__schema__.names():
        if name in ['last_compilation']:
            continue
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

            full_name = record.__prefix__ + name
            try:
                record.__registry__[full_name] = val
            except (AttributeError, KeyError) as ex:  # noqa
                # upgrade record on the fly, try to at least
                if not val:
                    continue
                if type(val) == bool:
                    record.__registry__.records[full_name] = Record(
                        field.Bool(title=u""), val)
                else:
                    raise


class OverrideFolderManager(object):

    def __init__(self, context):
        self.context = context
        persistent_directory = getUtility(IResourceDirectory, name="persistent")  # noqa
        if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
            persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)  # noqa
        self.container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]

    def save_file(self, filepath, data):
        resource_name, resource_filepath = filepath.split('/', 1)
        if resource_name not in self.container:
            self.container.makeDirectory(resource_name)
        folder = self.container[resource_name]
        if '.css' in resource_filepath:
            data = self.make_links_relative(filepath, data)
        folder.writeFile(resource_filepath, data)
        return folder[resource_filepath]

    def _rewrite_url(self, css_url, asset_url):
        """
        Pulled from:
        http://stackoverflow.com/questions/7469573/how-to-construct-relative-url-given-two-absolute-urls-in-python

        """
        base = urlparse(css_url)
        target = urlparse(asset_url)
        if base.netloc != target.netloc:
            return asset_url
        base_dir = '.' + posixpath.dirname(base.path)
        target = '.' + target.path
        return posixpath.relpath(target, start=base_dir)

    def make_links_relative(self, filepath, data):
        """
        make sure we don't write out any full urls.
        filepath will be something like foo/bar.css
        and the full real url will be something like http://site-url/++plone++foo/bar.css

        So we'll be everything relative the resource path.


        """
        site_url = self.context.absolute_url()
        full_resource_url = '%s/++plone++%s' % (site_url, filepath)
        for css_url in CSS_URL_REGEX.findall(data):
            if css_url.startswith("data:"):
                continue
            if css_url.find("data:image") > 0:
                continue

            css_url = css_url.lstrip('url(').rstrip(')').\
                strip('"').strip("'")
            if css_url.startswith(site_url):
                data = data.replace(css_url, self._rewrite_url(full_resource_url, css_url))

        return data

    def delete_file(self, filepath):
        resource_name, resource_filepath = filepath.split('/', 1)

        if resource_name not in self.container:
            return
        folder = self.container[resource_name]
        try:
            fi = folder[resource_filepath]
        except NotFound:
            return
        parent = self.get_parent(fi)
        del parent[fi.getId()]
        if filepath not in self.container:
            return
        folder = self.container[resource_name]
        try:
            fi = folder[resource_filepath]
        except NotFound:
            return
        parent = self.get_parent(fi)
        del parent[fi.getId()]

    def get_parent(self, item):
        path = '/'.join(item.getPhysicalPath()[:-1])
        return self.context.restrictedTraverse(path)

    def list_dir(self, container):
        if hasattr(container, 'listDirectory'):
            return container.listDirectory()
        else:
            return container.objectIds()


class ResourceRegistryControlPanelView(RequireJsView):

    def __call__(self):
        add_bundle_on_request(self.request, 'resourceregistry')
        req = self.request
        if req.REQUEST_METHOD == 'POST':
            action = req.get('action', '')
            method = action.replace('-', '_')
            if hasattr(self, method):
                return getattr(self, method)()
            else:
                return json.dumps({
                    'success': False,
                    'msg': 'Invalid action: ' + action
                })
        else:
            if RESOURCE_DEVELOPMENT_MODE:
                messages = IStatusMessage(self.request)
                messages.add(u"The FEDEV environment variable is set. No matter "
                             u"what settings are done here, all bundles will "
                             u"always be in development mode.", type=u"warn")
            return self.index()

    @property
    @memoize
    def registry(self):
        return getUtility(IRegistry)

    def update_registry_collection(self, itype, prefix, newdata):
        rdata = self.registry.collectionOfInterface(itype, prefix=prefix, check=False)
        for key, data in newdata.items():
            if key not in rdata:
                record = rdata.add(key)
            else:
                record = rdata[key]
            updateRecordFromDict(record, data)
        # remove missing ones
        for key in set(rdata.keys()) - set(newdata.keys()):
            del rdata[key]

    def save_registry(self):
        req = self.request

        self.update_registry_collection(
            IResourceRegistry, "plone.resources",
            json.loads(req.get('resources')))
        self.update_registry_collection(
            IBundleRegistry, "plone.bundles",
            json.loads(req.get('bundles')))

        if self.request.form.get('development', '').lower() == 'true':
            self.registry['plone.resources.development'] = True
        else:
            self.registry['plone.resources.development'] = False

        # it'd be difficult to know if the legacy bundle settings
        # changed or not so we need to just set the last import date
        # back so it gets re-built
        self.registry.records['plone.resources.last_legacy_import'].value = datetime.now()
        cookWhenChangingSettings(self.context)

        return json.dumps({
            'success': True
        })

    def save_file(self):
        req = self.request
        resource_path = req.form.get('filepath').split('++plone++')[-1]
        overrides = OverrideFolderManager(self.context)
        overrides.save_file(resource_path, req.form['data'])
        return json.dumps({
            'success': True
        })

    def delete_file(self):
        req = self.request
        resource_path = req.form.get('filepath').split('++plone++')[-1]
        overrides = OverrideFolderManager(self.context)
        overrides.delete_file(resource_path)

        if req.form.get('response') == 'html':
            return req.response.redirect(req.URL)
        return json.dumps({
            'success': True
        })

    def get_bundles(self):
        return self.registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles", check=False)

    def get_resources(self):
        return self.registry.collectionOfInterface(
            IResourceRegistry, prefix="plone.resources", check=False)

    def less_build_config(self):
        site_url = self.context.portal_url()
        bundles = self.get_bundles()
        bundle = self.request.get('bundle', None)
        resources = self.get_resources()
        less_files = []
        if bundle and bundle in bundles:
            bundle_obj = bundles[bundle]
            for resource in bundle_obj.resources:
                if resource in resources:
                    for css in resources[resource].css:
                        url = urlparse(css)
                        if url.netloc == '':
                            # Local
                            src = "%s/%s" % (site_url, css)
                        else:
                            src = "%s" % (css)

                        extension = url.path.split('.')[-1]
                        if extension == 'less':
                            less_files.append(src)
        return json.dumps({
            'less': less_files,
        })

    def js_build_config(self):
        (baseUrl, paths, shims) = self.get_requirejs_config()
        bundles = self.get_bundles()
        resources = self.get_resources()

        bundle = self.request.get('bundle', None)
        includes = []
        if bundle and bundle in bundles:
            bundle_obj = bundles[bundle]
            for resource_name in bundle_obj.resources:
                # need to check if this resource has a js file
                # it could just be a css resource
                try:
                    resource = resources[resource_name]
                    if resource.js:
                        includes.append(resource_name)
                except KeyError:
                    # skip if missing
                    pass
        return json.dumps({
            'include': includes,
            'shim': shims,
            'paths': paths,
            'wrapShim': True,
            'optimize': 'none'
        })

    def save_js_build(self):
        """
        'Â'
        """
        overrides = OverrideFolderManager(self.context)
        req = self.request
        filepath = 'static/%s-compiled.js' % req.form['bundle']

        data = req.form['data']
        overrides.save_file(filepath, data)
        bundle = self.get_bundles().get(req.form['bundle'])
        if bundle:
            bundle.last_compilation = datetime.now()
            bundle.jscompilation = '++plone++{}'.format(filepath)
        return json.dumps({
            'success': True,
            'filepath': '++plone++' + filepath
        })

    def save_less_build(self):
        overrides = OverrideFolderManager(self.context)
        req = self.request
        filepath = 'static/%s-compiled.css' % req.form['bundle']
        data = ''
        for key, value in req.form.items():
            if not key.startswith('data-'):
                continue
            if isinstance(value, basestring):
                value = [value]
            data += '\n'.join(value) + '\n'
        overrides.save_file(filepath, data)
        bundle = self.get_bundles().get(req.form['bundle'])
        if bundle:
            bundle.last_compilation = datetime.now()
            bundle.csscompilation = '++plone++{}'.format(filepath)
        return json.dumps({
            'success': True,
            'filepath': '++plone++' + filepath
        })

    def save_less_variables(self):
        data = {}
        for key, val in json.loads(self.request.form.get('data')).items():
            # need to convert to str: unicode
            data[key.encode('utf8')] = val
        self.registry['plone.lessvariables'] = data
        return json.dumps({
            'success': True
        })

    def save_pattern_options(self):
        data = {}
        for key, val in json.loads(self.request.form.get('data')).items():
            # need to convert to str: unicode
            data[key.encode('utf8')] = val
        self.registry['plone.patternoptions'] = data
        return json.dumps({
            'success': True
        })

    def get_overrides(self):
        overrides = OverrideFolderManager(self.context)

        def _read_folder(folder):
            files = []
            for filename in folder.listDirectory():
                try:
                    item = folder[filename]
                except NotFound:
                    continue
                if folder.isDirectory(filename):
                    files.extend(_read_folder(item))
                else:
                    files.append(item)
            return files
        files = _read_folder(overrides.container)
        results = []
        site_path = self.context.getPhysicalPath()
        for fi in files:
            path = fi.getPhysicalPath()
            rel_path = path[len(site_path) + 2:]
            results.append('++plone++%s/%s' % (
                rel_path[0], '/'.join(rel_path[1:])))
        return results

    def config(self):
        base_url = self.context.absolute_url()
        resources = self.get_resources()

        try:
            less_url = self.registry['plone.resources.lessc']
        except KeyError:
            less_url = '++plone++static/components/less/dist/less-1.7.4.min.js'
        try:
            rjs_url = resources['rjs'].js
        except KeyError:
            rjs_url = '++plone++static/components/r.js/dist/r.js'

        data = {
            'development': self.registry['plone.resources.development'],
            'lessvariables': self.registry['plone.lessvariables'],
            'resources': {},
            'bundles': {},
            'javascripts': {},
            'css': {},
            'baseUrl': base_url,
            'manageUrl': '%s/@@resourceregistry-controlpanel' % base_url,
            'lessUrl': '%s/%s' % (base_url, less_url),
            'lessConfigUrl': '%s/less-variables.js' % base_url,
            'rjsUrl': rjs_url,
            'patternoptions': self.registry['plone.patternoptions']
        }
        bundles = self.get_bundles()
        for key, resource in resources.items():
            data['resources'][key] = recordsToDict(resource)
        for key, bundle in bundles.items():
            data['bundles'][key] = recordsToDict(bundle)
        data['overrides'] = self.get_overrides()
        return json.dumps(data, cls=JSONEncoder)
