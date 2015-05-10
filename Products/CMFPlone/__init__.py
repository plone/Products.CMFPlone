from App.ImageFile import ImageFile
import os
import sys
import pkg_resources

__version__ = pkg_resources.require("Products.CMFPlone")[0].version


cmfplone_globals = globals()
this_module = sys.modules[__name__]
_marker = []

ADD_CONTENT_PERMISSION = 'Add portal content'
misc_ = {'plone_icon': ImageFile(
    os.path.join('skins', 'plone_images', 'logoIcon.png'),
    cmfplone_globals)}


def initialize(context):

    # Stuff has been moved from module level to this method for a
    # better separation of import and installation.
    # For the general user this change does not make a difference.
    # For test authors (and people who use parts of Plone only)
    # it does speed up import *significantly*.

    from AccessControl import ModuleSecurityInfo
    from AccessControl import allow_class
    from AccessControl import allow_module

    # protect OFS.ObjectManager
    ModuleSecurityInfo('OFS.ObjectManager').setDefaultAccess(0)
    ModuleSecurityInfo('OFS.ObjectManager').declareObjectPrivate()
    ModuleSecurityInfo('OFS.ObjectManager').declarePublic(
        'BeforeDeleteException')

    # allow logging
    ModuleSecurityInfo('logging').declarePublic('getLogger')
    from logging import Logger
    allow_class(Logger)

    # various small utils functions
    # added for unescaping view names in urls when finding selected action
    ModuleSecurityInfo('urllib').declarePublic('unquote')

    allow_module('Products.CMFPlone.utils')

    # For content_status_modify
    from Products.CMFCore.WorkflowCore import ObjectDeleted
    from Products.CMFCore.WorkflowCore import ObjectMoved
    from Products.CMFCore.WorkflowCore import WorkflowException
    ModuleSecurityInfo(
        'Products.CMFCore.WorkflowCore').declarePublic('ObjectDeleted')
    ModuleSecurityInfo(
        'Products.CMFCore.WorkflowCore').declarePublic('ObjectMoved')
    ModuleSecurityInfo(
        'Products.CMFCore.WorkflowCore').declarePublic('WorkflowException')
    allow_class(ObjectDeleted)
    allow_class(ObjectMoved)
    allow_class(WorkflowException)

    from Products.CMFPlone.PloneBatch import Batch
    allow_class(Batch)

    # Make Batch available at module level
    this_module.Batch = Batch

    ModuleSecurityInfo('StringIO').declarePublic('StringIO')
    from StringIO import StringIO
    allow_class(StringIO)

    # Make Unauthorized importable TTW
    ModuleSecurityInfo('AccessControl').declarePublic('Unauthorized')

    # Make Forbidden importable TTW
    ModuleSecurityInfo('zExceptions').declarePublic('Forbidden')

    # Make ConflictError importable TTW
    ModuleSecurityInfo('ZODB.POSException').declarePublic('ConflictError')

    # Make ZCTextIndex ParseError importable TTW
    ModuleSecurityInfo('Products.ZCTextIndex.ParseTree') \
        .declarePublic('ParseError')

    # Make DateTimeError importable TTW
    ModuleSecurityInfo('DateTime.interfaces').declarePublic('DateTimeError')
    ModuleSecurityInfo('DateTime.interfaces').declarePublic('SyntaxError')

    # BBB support for DateTime < 3
    ModuleSecurityInfo('DateTime.DateTime').declarePublic('DateTimeError')
    ModuleSecurityInfo('DateTime.DateTime').declarePublic('SyntaxError')

    # Make CopyError importable TTW
    ModuleSecurityInfo('OFS.CopySupport').declarePublic('CopyError')

    # Make AllowSendto importable TTW
    ModuleSecurityInfo('Products.CMFPlone.PloneTool') \
        .declarePublic('AllowSendto')

    # Make ZCatalog's mergeResults importable TTW
    ModuleSecurityInfo('Products.ZCatalog.Catalog') \
        .declarePublic('mergeResults')

    # Make the navtree constructs available TTW
    allow_module('Products.CMFPlone.browser.navtree')

    # Allow access to the exception in the folder_delete script
    from OFS.ObjectManager import BeforeDeleteException
    allow_module('OFS.ObjectManager')
    allow_class(BeforeDeleteException)

    # Make cgi.escape available TTW
    ModuleSecurityInfo('cgi').declarePublic('escape')

    # Apply monkey patches
    from Products.CMFPlone import patches  # noqa

    # Register unicode splitter w/ ZCTextIndex
    # pipeline registry
    from Products.CMFPlone import UnicodeSplitter  # noqa

    # Plone content

    # Usage of PloneFolder is discouraged.
    from Products.CMFPlone import PloneFolder

    contentClasses = (PloneFolder.PloneFolder, )
    contentConstructors = (PloneFolder.addPloneFolder, )

    # CMFCore tools
    from Products.CMFCore import CachingPolicyManager

    # Plone tools
    from Products.CMFPlone import PloneTool
    from Products.CMFPlone import MigrationTool
    from Products.CMFPlone import PloneControlPanel
    from Products.CMFPlone import WorkflowTool
    from Products.CMFPlone import URLTool
    from Products.CMFPlone import RegistrationTool
    from Products.CMFPlone import PropertiesTool
    from Products.CMFPlone import ActionsTool
    from Products.CMFPlone import TypesTool
    from Products.CMFPlone import CatalogTool
    from Products.CMFPlone import SkinsTool
    from Products.CMFPlone import QuickInstallerTool
    from Products.CMFPlone import TranslationServiceTool

    tools = (
        PloneTool.PloneTool,
        WorkflowTool.WorkflowTool,
        CachingPolicyManager.CachingPolicyManager,
        PropertiesTool.PropertiesTool,
        MigrationTool.MigrationTool,
        PloneControlPanel.PloneControlPanel,
        RegistrationTool.RegistrationTool,
        URLTool.URLTool,
        ActionsTool.ActionsTool,
        TypesTool.TypesTool,
        CatalogTool.CatalogTool,
        SkinsTool.SkinsTool,
        QuickInstallerTool.QuickInstallerTool,
        TranslationServiceTool.TranslationServiceTool,
    )

    from Products.CMFCore.utils import ContentInit
    from Products.CMFPlone.utils import ToolInit

    # Register tools and content
    ToolInit(
        'Plone Tool',
        tools=tools,
        icon='tool.gif',
    ).initialize(context)

    ContentInit(
        'Plone Content',
        content_types=contentClasses,
        permission=ADD_CONTENT_PERMISSION,
        extra_constructors=contentConstructors,
    ).initialize(context)

    from AccessControl.Permissions import view_management_screens
    from Products.CMFPlone.Portal import PloneSite
    from Products.CMFPlone.factory import zmi_constructor
    context.registerClass(
        instance_class=PloneSite,
        permission=view_management_screens,
        constructors=(zmi_constructor, ),
    )

    from plone.app.folder import nogopip
    context.registerClass(
        nogopip.GopipIndex,
        permission='Add Pluggable Index',
        constructors=(nogopip.manage_addGopipForm,
                      nogopip.manage_addGopipIndex),
        icon='index.gif',
        visibility=None
    )


# Import PloneMessageFactory to create messages in the plone domain
from zope.i18nmessageid import MessageFactory
PloneMessageFactory = MessageFactory('plone')

# Import PloneLocalesMessageFactory to create messages in the
# plonelocales domain
from zope.i18nmessageid import MessageFactory
PloneLocalesMessageFactory = MessageFactory('plonelocales')
