import sys
import os
from App.ImageFile import ImageFile

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
    from AccessControl import allow_module, allow_class

    # allow logging
    ModuleSecurityInfo('logging').declarePublic('getLogger')
    from logging import Logger
    allow_class(Logger)

    # Register kss extension to allow it used from fs skins
    from Products.CMFCore.DirectoryView import registerFileExtension
    from Products.CMFCore.FSFile import FSFile
    registerFileExtension('kss', FSFile)

    # various small utils functions
    # added for unescaping view names in urls when finding selected action
    ModuleSecurityInfo('urllib').declarePublic('unquote')

    allow_module('Products.CMFPlone.utils')

    # For content_status_modify
    from Products.CMFCore.WorkflowCore import ObjectMoved, ObjectDeleted, \
                                              WorkflowException
    ModuleSecurityInfo('Products.CMFCore.WorkflowCore').declarePublic('ObjectMoved')
    ModuleSecurityInfo('Products.CMFCore.WorkflowCore').declarePublic('ObjectDeleted')
    ModuleSecurityInfo('Products.CMFCore.WorkflowCore').declarePublic('WorkflowException')
    allow_class(ObjectMoved)
    allow_class(ObjectDeleted)
    allow_class(WorkflowException)

    from PloneBatch import Batch
    allow_class(Batch)

    # Make Batch available at module level
    this_module.Batch = Batch

    from StringIO import StringIO
    allow_class(StringIO)

    # Make Unauthorized importable TTW
    ModuleSecurityInfo('AccessControl').declarePublic('Unauthorized')

    # Make Forbidden importable TTW
    ModuleSecurityInfo('zExceptions').declarePublic('Forbidden')

    # Make ConflictError importable TTW
    ModuleSecurityInfo('ZODB.POSException').declarePublic('ConflictError')

    # Make ZCTextIndex ParseError importable TTW
    ModuleSecurityInfo('Products.ZCTextIndex.ParseTree').declarePublic('ParseError')

    # Make DateTimeError importable TTW
    ModuleSecurityInfo('DateTime.interfaces').declarePublic('DateTimeError')
    ModuleSecurityInfo('DateTime.interfaces').declarePublic('SyntaxError')

    # BBB support for DateTime < 3
    ModuleSecurityInfo('DateTime.DateTime').declarePublic('DateTimeError')
    ModuleSecurityInfo('DateTime.DateTime').declarePublic('SyntaxError')

    # Make CopyError importable TTW
    ModuleSecurityInfo('OFS.CopySupport').declarePublic('CopyError')

    # Make DiscussionNotAllowed importable TTW
    ModuleSecurityInfo('Products.CMFDefault.DiscussionTool').declarePublic('DiscussionNotAllowed')

    # Make AllowSendto importable TTW
    ModuleSecurityInfo('Products.CMFPlone.PloneTool').declarePublic('AllowSendto')

    # Make ZCatalog's mergeResults importable TTW
    ModuleSecurityInfo('Products.ZCatalog.Catalog').declarePublic('mergeResults')

    # Make the navtree constructs available TTW
    allow_module('Products.CMFPlone.browser.navtree')

    # Allow access to the exception in the folder_delete script
    from OFS.ObjectManager import BeforeDeleteException
    allow_module('OFS.ObjectManager')
    allow_class(BeforeDeleteException)

    # Make cgi.escape available TTW
    ModuleSecurityInfo('cgi').declarePublic('escape')

    # Apply monkey patches
    import patches

    # Register unicode splitter w/ ZCTextIndex
    # pipeline registry
    import UnicodeSplitter

    # Plone content

    # Usage of PloneFolder is discouraged.
    import PloneFolder

    contentClasses = (PloneFolder.PloneFolder, )
    contentConstructors = (PloneFolder.addPloneFolder, )

    # CMFCore and CMFDefault tools
    from Products.CMFCore import CachingPolicyManager

    # Plone tools
    import PloneTool
    import FactoryTool
    import InterfaceTool
    import MigrationTool
    import PloneControlPanel
    import WorkflowTool
    import URLTool
    import MetadataTool
    import RegistrationTool
    import SyndicationTool
    import PropertiesTool
    import ActionsTool
    import TypesTool
    import UndoTool
    import CatalogTool
    import SkinsTool
    import DiscussionTool
    import CalendarTool
    import ActionIconsTool
    import QuickInstallerTool
    import TranslationServiceTool

    tools = (PloneTool.PloneTool,
             WorkflowTool.WorkflowTool,
             CachingPolicyManager.CachingPolicyManager,
             FactoryTool.FactoryTool,
             PropertiesTool.PropertiesTool,
             MigrationTool.MigrationTool,
             InterfaceTool.InterfaceTool,
             PloneControlPanel.PloneControlPanel,
             RegistrationTool.RegistrationTool,
             URLTool.URLTool,
             MetadataTool.MetadataTool,
             ActionsTool.ActionsTool,
             TypesTool.TypesTool,
             UndoTool.UndoTool,
             SyndicationTool.SyndicationTool,
             CatalogTool.CatalogTool,
             SkinsTool.SkinsTool,
             DiscussionTool.DiscussionTool,
             ActionIconsTool.ActionIconsTool,
             CalendarTool.CalendarTool,
             QuickInstallerTool.QuickInstallerTool,
             TranslationServiceTool.TranslationServiceTool,
            )

    from Products.CMFCore.utils import ContentInit
    from Products.CMFPlone.utils import ToolInit

    # Register tools and content
    ToolInit('Plone Tool',
             tools=tools,
             icon='tool.gif',
             ).initialize(context)

    ContentInit('Plone Content',
                content_types=contentClasses,
                permission=ADD_CONTENT_PERMISSION,
                extra_constructors=contentConstructors,
                ).initialize(context)

    from Products.CMFPlone.Portal import PloneSite
    from Products.CMFPlone.factory import zmi_constructor
    from AccessControl.Permissions import view_management_screens
    context.registerClass(
        instance_class=PloneSite,
        permission=view_management_screens,
        constructors=(zmi_constructor, ),
    )

    from plone.app.folder import nogopip
    context.registerClass(nogopip.GopipIndex,
        permission = 'Add Pluggable Index',
        constructors = (nogopip.manage_addGopipForm,
                        nogopip.manage_addGopipIndex),
        icon = 'index.gif',
        visibility = None)


# Import PloneMessageFactory to create messages in the plone domain
from zope.i18nmessageid import MessageFactory
PloneMessageFactory = MessageFactory('plone')

# Import PloneLocalesMessageFactory to create messages in the plonelocales domain
from zope.i18nmessageid import MessageFactory
PloneLocalesMessageFactory = MessageFactory('plonelocales')
