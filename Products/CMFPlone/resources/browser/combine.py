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
    production_folder = container[PRODUCTION_RESOURCE_DIRECTORY]
    timestamp = production_folder.readFile('timestamp.txt')
    return "%s/++unique++%s" % (
        PRODUCTION_RESOURCE_DIRECTORY, timestamp)


def get_resource(context, path):
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
        if bundle.merge_with == meta_bundle:
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
        if bundle.merge_with == meta_bundle:
            resources.append(get_resource(context, bundle.csscompilation))

    fi = StringIO()
    for script in resources:
        fi.write(script + '\n')
    folder.writeFile(meta_bundle + ".css", fi)


def combine_bundles(context):
    persistent_directory = queryUtility(IResourceDirectory, name="persistent")
    if persistent_directory is None:
        return
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
        persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
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
