# -*- coding: utf-8 -*-
from Acquisition import aq_base
from datetime import datetime
from io import BytesIO
from plone.registry.interfaces import IRegistry
from plone.resource.file import FilesystemFile
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME  # noqa
from zExceptions import NotFound
from zope.component import getUtility
from zope.component import queryUtility

import logging
import re
import six


PRODUCTION_RESOURCE_DIRECTORY = 'production'
logger = logging.getLogger(__name__)


def get_production_resource_directory():
    persistent_directory = queryUtility(IResourceDirectory, name='persistent')
    if persistent_directory is None:
        return ''
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
    try:
        production_folder = container[PRODUCTION_RESOURCE_DIRECTORY]
    except NotFound:
        return '%s/++unique++1' % PRODUCTION_RESOURCE_DIRECTORY
    if 'timestamp.txt' not in production_folder:
        return '%s/++unique++1' % PRODUCTION_RESOURCE_DIRECTORY
    timestamp = production_folder.readFile('timestamp.txt')
    if not six.PY2 and isinstance(timestamp, six.binary_type):
        timestamp = timestamp.decode()
    return '%s/++unique++%s' % (
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
        logger.warn(u'Could not find resource {0}. You may have to create it first.'.format(path))  # noqa
        return

    if isinstance(resource, FilesystemFile):
        (directory, sep, filename) = path.rpartition('/')
        return context.unrestrictedTraverse(directory).readFile(filename)

    # calling the resource may modify the header, i.e. the content-type.
    # we do not want this, so keep the original header intact.
    response_before = context.REQUEST.response
    context.REQUEST.response = response_before.__class__()
    if hasattr(aq_base(resource), 'GET'):
        # for FileResource
        result = resource.GET()
    else:
        # any BrowserView
        result = resource()
    context.REQUEST.response = response_before
    return result


def write_js(context, folder, meta_bundle):
    registry = getUtility(IRegistry)
    resources = []

    # default resources
    if (
        meta_bundle == 'default' and
        registry.records.get('plone.resources/jquery.js')
    ):
        resources.append(
            get_resource(
                context,
                registry.records['plone.resources/jquery.js'].value
            )
        )
        resources.append(
            get_resource(
                context,
                registry.records['plone.resources.requirejs'].value
            )
        )
        resources.append(
            get_resource(
                context,
                registry.records['plone.resources.configjs'].value
            )
        )

    # bundles
    bundles = registry.collectionOfInterface(
        IBundleRegistry,
        prefix='plone.bundles',
        check=False
    )
    for bundle in bundles.values():
        if bundle.merge_with == meta_bundle and bundle.jscompilation:
            resource = get_resource(context, bundle.jscompilation)
            if not resource:
                continue
            resources.append(resource)

    fi = BytesIO()
    for script in resources:
        if not isinstance(script, six.binary_type):
            script = script.encode()
        fi.write((script + b'\n'))
    folder.writeFile(meta_bundle + '.js', fi)


def write_css(context, folder, meta_bundle):
    registry = getUtility(IRegistry)
    resources = []

    bundles = registry.collectionOfInterface(
        IBundleRegistry,
        prefix='plone.bundles',
        check=False
    )
    for bundle in bundles.values():
        if bundle.merge_with == meta_bundle and bundle.csscompilation:
            css = get_resource(context, bundle.csscompilation)
            if not css:
                continue
            (path, sep, filename) = bundle.csscompilation.rpartition('/')
            # Process relative urls:
            # we prefix with current resource path any url not starting with
            # '/' or http: or data:
            if not isinstance(path, six.binary_type):
                path = path.encode()
            css = re.sub(
                br"""(url\(['"]?(?!['"]?([a-z]+:|\/)))""",
                br'\1%s/' % path,
                css)
            resources.append(css)

    fi = BytesIO()
    for script in resources:
        if not isinstance(script, six.binary_type):
            script = script.encode()
        fi.write((script + b'\n'))
    folder.writeFile(meta_bundle + '.css', fi)


def get_override_directory(context):
    persistent_directory = queryUtility(IResourceDirectory, name='persistent')
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
    fi = BytesIO()
    fi.write(datetime.now().isoformat().encode())
    production_folder.writeFile('timestamp.txt', fi)

    # generate new combined bundles
    write_js(context, production_folder, 'default')
    write_js(context, production_folder, 'logged-in')
    write_css(context, production_folder, 'default')
    write_css(context, production_folder, 'logged-in')
