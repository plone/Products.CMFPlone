import logging
import re
from collections import OrderedDict
from datetime import datetime
from StringIO import StringIO

from Acquisition import aq_base
from plone.registry.interfaces import IRegistry
from plone.resource.file import FilesystemFile
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces.resources import \
    OVERRIDE_RESOURCE_DIRECTORY_NAME  # noqa
from zExceptions import NotFound
from zope.component import getUtility, queryUtility

PRODUCTION_RESOURCE_DIRECTORY = "production"
logger = logging.getLogger(__name__)


def get_production_resource_directory():
    persistent_directory = queryUtility(IResourceDirectory, name="persistent")
    if persistent_directory is None:
        return ''
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
    try:
        production_folder = container[PRODUCTION_RESOURCE_DIRECTORY]
    except NotFound:
        return "%s/++unique++1" % PRODUCTION_RESOURCE_DIRECTORY
    if 'timestamp.txt' not in production_folder:
        return "%s/++unique++1" % PRODUCTION_RESOURCE_DIRECTORY
    timestamp = production_folder.readFile('timestamp.txt')
    return "%s/++unique++%s" % (
        PRODUCTION_RESOURCE_DIRECTORY, timestamp)


def get_resource(context, path):
    if path.startswith('++plone++'):
        # ++plone++ resources can be customized, we return their override
        # value if any
        overrides = get_override_directory(context)
        filepath = path[9:]
        if overrides.isFile(filepath):
            return overrides.readFile(filepath)

    try:
        resource = context.unrestrictedTraverse(path)
    except NotFound:
        logger.warn(u"Could not find resource {0}. You may have to create it first.".format(path))  # noqa
        return

    if isinstance(resource, FilesystemFile):
        (directory, sep, filename) = path.rpartition('/')
        return context.unrestrictedTraverse(directory).readFile(filename)
    else:
        if hasattr(aq_base(resource), 'GET'):
            # for FileResource
            return resource.GET()
        else:
            # any BrowserView
            return resource()


class MetaBundleWriter(object):

    def __init__(self, context, folder, name):
        self.context = context
        self.folder = folder
        self.name = name
        self.js_resources = OrderedDict()
        self.css_resources = OrderedDict()
        self.registry = getUtility(IRegistry)
        self.bundles = self.registry.collectionOfInterface(
            IBundleRegistry, prefix="plone.bundles", check=False)

    def write_js(self):

        # default resources
        if self.name == 'default' and self.registry.records.get(
            'plone.resources/jquery.js'
        ):
            self.js_resources['_jquery'] = get_resource(
                self.context,
                self.registry.records['plone.resources/jquery.js'].value)
            self.js_resources['_requirejs'] = get_resource(
                self.context,
                self.registry.records['plone.resources.requirejs'].value)
            self.js_resources['_configjs'] = get_resource(
                self.context,
                self.registry.records['plone.resources.configjs'].value)

        # bundles
        for name, bundle in self.bundles.items():
            self.load_js_bundle(name, bundle)

        self._write_out(self.js_resources, '.js')

    def load_js_bundle(self, name, bundle, depth=0):
        if depth > 10:
            # recursion detection
            return
        if bundle.merge_with != self.name:
            return
        if bundle.jscompilation:
            if bundle.depends and bundle.depends in self.bundles:
                self.load_js_bundle(
                    bundle.depends, self.bundles[bundle.depends], depth + 1)
            if name in self.js_resources:
                return
            resource = get_resource(self.context, bundle.jscompilation)
            if not resource:
                return
            self.js_resources[name] = resource

    def _write_out(self, resources, postfix):
        fi = StringIO()
        for bname, script in resources.items():
            fi.write('''
// Start Bundle: {0}
{1}
// End Bundle: {2}
'''.format(bname, script, bname))
        self.folder.writeFile(self.name + postfix, fi)
        resources.clear()

    def load_css_bundle(self, name, bundle, depth=0):
        if depth > 10:
            # recursion detection
            return

        if bundle.merge_with != self.name:
            return

        if bundle.csscompilation:
            if bundle.depends and bundle.depends in self.bundles:
                self.load_css_bundle(
                    bundle.depends, self.bundles[bundle.depends], depth + 1)
            if name in self.css_resources:
                return

            css = get_resource(self.context, bundle.csscompilation)
            if not css:
                return
            (path, sep, filename) = bundle.csscompilation.rpartition('/')
            # Process relative urls:
            # we prefix with current resource path any url not starting with
            # '/' or http: or data:
            css = re.sub(
                r"""(url\(['"]?(?!['"]?([a-z]+:|\/)))""",
                r'\1%s/' % path,
                css)
            self.css_resources[name] = css

    def write_css(self):
        for name, bundle in self.bundles.items():
            self.load_css_bundle(name, bundle)

        self._write_out(self.css_resources, '.css')


def get_override_directory(context):
    persistent_directory = queryUtility(IResourceDirectory, name="persistent")
    if persistent_directory is None:
        return
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
        persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
    return persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]


def combine_bundles(context):
    container = get_override_directory(context)
    if PRODUCTION_RESOURCE_DIRECTORY not in container:
        container.makeDirectory(PRODUCTION_RESOURCE_DIRECTORY)
    production_folder = container[PRODUCTION_RESOURCE_DIRECTORY]

    # store timestamp
    fi = StringIO()
    fi.write(datetime.now().isoformat())
    production_folder.writeFile("timestamp.txt", fi)

    # generate new combined bundles
    default_writer = MetaBundleWriter(
        context, production_folder, 'default')
    default_writer.write_js()
    logged_in_writer = MetaBundleWriter(
        context, production_folder, 'logged-in')
    logged_in_writer.write_js()
    default_writer.write_css()
    logged_in_writer.write_css()
