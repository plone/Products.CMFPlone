from Acquisition import aq_base
from plone.registry.interfaces import IRegistry
from plone.resource.file import FilesystemFile
from plone.resource.interfaces import IResourceDirectory
from Products.CMFPlone.interfaces import IBundleRegistry
from Products.CMFPlone.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME
from zExceptions import NotFound
from zope.component import getUtility
from zope.component import queryUtility

import logging


PRODUCTION_RESOURCE_DIRECTORY = "production"
logger = logging.getLogger(__name__)


def get_production_resource_directory():
    persistent_directory = queryUtility(IResourceDirectory, name="persistent")
    if persistent_directory is None:
        return ""
    container = persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
    try:
        production_folder = container[PRODUCTION_RESOURCE_DIRECTORY]
    except NotFound:
        return "%s/++unique++1" % PRODUCTION_RESOURCE_DIRECTORY
    if "timestamp.txt" not in production_folder:
        return "%s/++unique++1" % PRODUCTION_RESOURCE_DIRECTORY
    timestamp = production_folder.readFile("timestamp.txt")
    if isinstance(timestamp, bytes):
        timestamp = timestamp.decode()
    return "{}/++unique++{}".format(PRODUCTION_RESOURCE_DIRECTORY, timestamp)


def get_resource(context, path):
    if path.startswith("++plone++"):
        # ++plone++ resources can be customized, we return their override
        # value if any
        overrides = get_override_directory(context)
        filepath = path[9:]
        if overrides.isFile(filepath):
            return overrides.readFile(filepath)

    try:
        resource = context.unrestrictedTraverse(path)
    except (NotFound, AttributeError):
        logger.warning(
            f"Could not find resource {path}. You may have to create it first."
        )  # noqa
        return

    if isinstance(resource, FilesystemFile):
        (directory, sep, filename) = path.rpartition("/")
        return context.unrestrictedTraverse(directory).readFile(filename)

    # calling the resource may modify the header, i.e. the content-type.
    # we do not want this, so keep the original header intact.
    response_before = context.REQUEST.response
    context.REQUEST.response = response_before.__class__()
    if hasattr(aq_base(resource), "GET"):
        # for FileResource
        result = resource.GET()
    else:
        # any BrowserView
        result = resource()
    context.REQUEST.response = response_before
    return result


def get_override_directory(context):
    persistent_directory = queryUtility(IResourceDirectory, name="persistent")
    if persistent_directory is None:
        return
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
        persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
    return persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]
