import re
from zExceptions import NotFound
from Acquisition import aq_base
from datetime import datetime
from plone.registry.interfaces import IRegistry
from plone.resource.file import FilesystemFile
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces.resources import (
    OVERRIDE_RESOURCE_DIRECTORY_NAME,
)
from StringIO import StringIO
from zope.component import getUtility
from zope.component import queryUtility

PRODUCTION_RESOURCE_DIRECTORY = "production"


def get_production_resource_directory():
    persistent_directory = queryUtility(IResourceDirectory, name="persistent")
    if persistent_directory is None:
        return ''
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
    try:
        production_folder = container[PRODUCTION_RESOURCE_DIRECTORY]
    except NotFound:
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

    resource = context.unrestrictedTraverse(path)
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


def write_js(context, folder, meta_bundle):
    registry = getUtility(IRegistry)
    resources = []

    # default resources
    if meta_bundle == 'default' and registry.records.get(
        'plone.resources/jquery.js'
    ):
        resources.append(get_resource(context,
            registry.records['plone.resources/jquery.js'].value))
        resources.append(get_resource(context,
            registry.records['plone.resources.requirejs'].value))
        resources.append(get_resource(context,
            registry.records['plone.resources.configjs'].value))

    # bundles
    bundles = registry.collectionOfInterface(
        IBundleRegistry, prefix="plone.bundles", check=False)
    for bundle in bundles.values():
        if bundle.merge_with == meta_bundle and bundle.jscompilation:
            resources.append(get_resource(context, bundle.jscompilation))

    fi = StringIO()
    for script in resources:
        fi.write(script + '\n')
    folder.writeFile(meta_bundle + ".js", fi)


def write_css(context, folder, meta_bundle):
    registry = getUtility(IRegistry)
    resources = []

    bundles = registry.collectionOfInterface(
        IBundleRegistry, prefix="plone.bundles", check=False)
    for bundle in bundles.values():
        if bundle.merge_with == meta_bundle and bundle.csscompilation:
            css = get_resource(context, bundle.csscompilation)
            (path, sep, filename) = bundle.csscompilation.rpartition('/')
            # Process relative urls:
            # we prefix with current resource path any url not starting with
            # '/' or http: or data:
            css = re.sub(
                r"""(url\(['"]?(?!['"]?([a-z]+:|\/)))""",
                r'\1%s/' % path,
                css)
            resources.append(css)

    fi = StringIO()
    for script in resources:
        fi.write(script + '\n')
    folder.writeFile(meta_bundle + ".css", fi)


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
    write_js(context, production_folder, 'default')
    write_js(context, production_folder, 'logged-in')
    write_css(context, production_folder, 'default')
    write_css(context, production_folder, 'logged-in')
