from App.ImageFile import ImageFile
from importlib.metadata import version as dist_version

import os
import sys
import warnings
import zope.deferredimport


__version__ = dist_version("Products.CMFPlone")

if __version__ < "7":
    # This sets SKIP_PTA to skip the check for
    # Publication through acquisition in Plone 6.
    # Please remove this code block when can.
    from Products.CMFCore.explicitacquisition import PTA_ENV_KEY

    import Products.CMFCore.explicitacquisition

    os.environ[PTA_ENV_KEY] = os.environ.get(PTA_ENV_KEY, "false")
    # Importing (from) the module sets SKIP_PTA. We need to override that too.
    Products.CMFCore.explicitacquisition.SKIP_PTA = os.environ[PTA_ENV_KEY] == "false"

cmfplone_globals = globals()
this_module = sys.modules[__name__]
_marker = []

ADD_CONTENT_PERMISSION = "Add portal content"
misc_ = {
    "plone_icon": ImageFile(
        os.path.join("skins", "plone_images", "logoIcon.png"), cmfplone_globals
    )
}

zope.deferredimport.initialize()
zope.deferredimport.deprecated(
    "Import from plone.base instead (to be removed in Plone 7)",
    PloneMessageFactory="plone.base:PloneMessageFactory",
    PloneLocalesMessageFactory="plone.base:PloneMessageFactory",
)
zope.deferredimport.deprecated(
    "Import from plone.app.discussion.interfaces instead (to be removed in Plone 7)",
    DISCUSSION_ANNOTATION_KEY="plone.app.discussion.interfaces:DISCUSSION_ANNOTATION_KEY",
)


def initialize(context):
    # Stuff has been moved from module level to this method for a
    # better separation of import and installation.
    # For the general user this change does not make a difference.
    # For test authors (and people who use parts of Plone only)
    # it does speed up import *significantly*.

    from AccessControl import allow_class
    from AccessControl import ModuleSecurityInfo

    # Allow importing and catching BeforeDeleteException in untrusted code.
    ModuleSecurityInfo("OFS.ObjectManager").declarePublic("BeforeDeleteException")
    from OFS.ObjectManager import BeforeDeleteException

    allow_class(BeforeDeleteException)

    # allow logging
    ModuleSecurityInfo("logging").declarePublic("getLogger")
    from logging import Logger

    allow_class(Logger)

    # various small utils functions
    # added for unescaping view names in urls when finding selected action
    ModuleSecurityInfo("urllib").declarePublic("unquote")

    # Declare the public names of the utils module one by one.
    # Never open the whole module: it would publish all its imports.
    utils_security = ModuleSecurityInfo("Products.CMFPlone.utils")
    for name in (
        "normalizeString",
        "get_portal",
        "getSiteLogo",
        "typesToList",
        "safe_unicode",
        "safe_encode",
        "safe_nativestring",
        "webdav_enabled",
        "parent",
        "bodyfinder",
        "createBreadCrumbs",
        "createSiteMap",
        "isExpired",
        "versionTupleFromString",
        "getFSVersionTuple",
        "tuplize",
        "flatten",
        "ajax_load_url",
        "log",
        "log_exc",
        "log_deprecated",
        "base_hasattr",
        "safe_hasattr",
        "safe_callable",
        "safe_text",
        "safe_bytes",
        "safeToInt",
        "transaction_note",
        "pretty_title_or_id",
        "human_readable_size",
        "check_id",
    ):
        utils_security.declarePublic(name)

    # For content_status_modify
    from Products.CMFCore.WorkflowCore import ObjectDeleted
    from Products.CMFCore.WorkflowCore import ObjectMoved
    from Products.CMFCore.WorkflowCore import WorkflowException

    ModuleSecurityInfo("Products.CMFCore.WorkflowCore").declarePublic("ObjectDeleted")
    ModuleSecurityInfo("Products.CMFCore.WorkflowCore").declarePublic("ObjectMoved")
    ModuleSecurityInfo("Products.CMFCore.WorkflowCore").declarePublic(
        "WorkflowException"
    )
    allow_class(ObjectDeleted)
    allow_class(ObjectMoved)
    allow_class(WorkflowException)

    # bbb - remove in Plone 7
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        from Products.CMFPlone.PloneBatch import Batch
    allow_class(Batch)

    # Make Batch available at module level
    this_module.Batch = Batch

    ModuleSecurityInfo("StringIO").declarePublic("StringIO")

    # Make Unauthorized importable TTW
    ModuleSecurityInfo("AccessControl").declarePublic("Unauthorized")

    # Make Forbidden importable TTW
    ModuleSecurityInfo("zExceptions").declarePublic("Forbidden")

    # Make ConflictError importable TTW
    ModuleSecurityInfo("ZODB.POSException").declarePublic("ConflictError")

    # Make ZCTextIndex ParseError importable TTW
    ModuleSecurityInfo("Products.ZCTextIndex.ParseTree").declarePublic("ParseError")

    # Make DateTimeError importable TTW
    ModuleSecurityInfo("DateTime.interfaces").declarePublic("DateTimeError")
    ModuleSecurityInfo("DateTime.interfaces").declarePublic("SyntaxError")

    # BBB support for DateTime < 3
    ModuleSecurityInfo("DateTime.DateTime").declarePublic("DateTimeError")
    ModuleSecurityInfo("DateTime.DateTime").declarePublic("SyntaxError")

    # Make CopyError importable TTW
    ModuleSecurityInfo("OFS.CopySupport").declarePublic("CopyError")

    # Make AllowSendto importable TTW
    ModuleSecurityInfo("Products.CMFPlone.PloneTool").declarePublic("AllowSendto")

    # Make ZCatalog's mergeResults importable TTW
    ModuleSecurityInfo("Products.ZCatalog.Catalog").declarePublic("mergeResults")

    # Make the navtree constructs available TTW
    navtree_security = ModuleSecurityInfo("Products.CMFPlone.browser.navtree")
    for name in (
        "NavtreeQueryBuilder",
        "SitemapQueryBuilder",
        "SitemapNavtreeStrategy",
        "DefaultNavtreeStrategy",
        "NavtreeStrategyBase",
    ):
        navtree_security.declarePublic(name)

    # Make cgi.escape available TTW
    ModuleSecurityInfo("cgi").declarePublic("escape")

    # Make warnings available TTW
    ModuleSecurityInfo("warnings").declarePublic("warn")

    # Apply monkey patches
    # CMFCore tools
    from Products.CMFCore import CachingPolicyManager

    # Plone tools
    # Register unicode splitter w/ ZCTextIndex
    # pipeline registry
    from Products.CMFPlone import ActionsTool
    from Products.CMFPlone import CatalogTool
    from Products.CMFPlone import MigrationTool
    from Products.CMFPlone import patches  # noqa
    from Products.CMFPlone import PloneControlPanel
    from Products.CMFPlone import PloneTool
    from Products.CMFPlone import RegistrationTool
    from Products.CMFPlone import SkinsTool
    from Products.CMFPlone import TranslationServiceTool
    from Products.CMFPlone import TypesTool
    from Products.CMFPlone import UnicodeSplitter  # noqa
    from Products.CMFPlone import URLTool
    from Products.CMFPlone import WorkflowTool

    tools = (
        PloneTool.PloneTool,
        WorkflowTool.WorkflowTool,
        CachingPolicyManager.CachingPolicyManager,
        MigrationTool.MigrationTool,
        PloneControlPanel.PloneControlPanel,
        RegistrationTool.RegistrationTool,
        URLTool.URLTool,
        ActionsTool.ActionsTool,
        TypesTool.TypesTool,
        CatalogTool.CatalogTool,
        SkinsTool.SkinsTool,
        TranslationServiceTool.TranslationServiceTool,
    )

    from Products.CMFPlone.utils import ToolInit

    # Register tools and content
    ToolInit(
        "Plone Tool",
        tools=tools,
        icon="tool.gif",
    ).initialize(context)

    from AccessControl.Permissions import view_management_screens
    from Products.CMFPlone.factory import zmi_constructor
    from Products.CMFPlone.Portal import PloneSite

    context.registerClass(
        instance_class=PloneSite,
        permission=view_management_screens,
        constructors=(zmi_constructor,),
    )

    from plone.folder import nogopip

    context.registerClass(
        nogopip.GopipIndex,
        permission="Add Pluggable Index",
        constructors=(nogopip.manage_addGopipForm, nogopip.manage_addGopipIndex),
        icon="index.gif",
        visibility=None,
    )


# Apply early monkey patches.  For these patches, it is too late if we do this
# in the initialize method.
from Products.CMFPlone import earlypatches  # noqa
