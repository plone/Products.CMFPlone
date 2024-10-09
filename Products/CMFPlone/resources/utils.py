from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from OFS.Image import File
from plone.base.interfaces.resources import OVERRIDE_RESOURCE_DIRECTORY_NAME
from plone.resource.file import FilesystemFile
from plone.resource.interfaces import IResourceDirectory
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
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
    return f"{PRODUCTION_RESOURCE_DIRECTORY}/++unique++{timestamp}"


def get_resource(context, path):
    if path.startswith("++plone++"):
        # ++plone++ resources can be customized, we return their override
        # value if any
        overrides = get_override_directory(context)
        filepath = path[9:]
        if overrides.isFile(filepath):
            return overrides.readFile(filepath)

    if "?" in path:
        # Example from plone.session:
        # "acl_users/session/refresh?session_refresh=true&type=css&minutes=5"
        # Traversing will not work then.  In this example we could split on "?"
        # and traverse to the first part, acl_users/session/refresh, but this
        # gives a function, and this fails when we call it below, missing a
        # REQUEST argument
        return
    try:
        resource = context.unrestrictedTraverse(path)
    except (NotFound, AttributeError, KeyError):
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
    elif isinstance(resource, File):
        # An OFS.Image.File object
        result = resource.data
    elif callable(resource):
        # any BrowserView
        result = resource()
    else:
        logger.info("Cannot get data from resource %r", resource)
        result = b""
    context.REQUEST.response = response_before
    return result


def get_override_directory(context):
    persistent_directory = queryUtility(IResourceDirectory, name="persistent")
    if persistent_directory is None:
        return
    if OVERRIDE_RESOURCE_DIRECTORY_NAME not in persistent_directory:
        persistent_directory.makeDirectory(OVERRIDE_RESOURCE_DIRECTORY_NAME)
    return persistent_directory[OVERRIDE_RESOURCE_DIRECTORY_NAME]


def evaluateExpression(expression, context):
    """Evaluate an object's TALES condition to see if it should be
    displayed."""
    try:
        if expression.text and context is not None:
            portal = getToolByName(context, "portal_url").getPortalObject()

            # Find folder (code courtesy of CMFCore.ActionsTool)
            if context is None or not hasattr(context, "aq_base"):
                folder = portal
            else:
                folder = context
                # Search up the containment hierarchy until we find an
                # object that claims it's PrincipiaFolderish.
                while folder is not None:
                    if getattr(aq_base(folder), "isPrincipiaFolderish", 0):
                        # found it.
                        break
                    else:
                        folder = aq_parent(aq_inner(folder))

            __traceback_info__ = (folder, portal, context, expression)
            ec = createExprContext(folder, portal, context)
            # add 'context' as an alias for 'object'
            ec.setGlobal("context", context)
            return expression(ec)
        return True
    except AttributeError:
        return True
