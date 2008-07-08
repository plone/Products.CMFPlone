import sys
import os
import Globals

cmfplone_globals = globals()
this_module = sys.modules[ __name__ ]
_marker = []

ADD_CONTENT_PERMISSION = 'Add portal content'

misc_ = {'plone_icon': Globals.ImageFile(
                       os.path.join('skins', 'plone_images', 'logoIcon.gif'),
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

    # For form validation bits
    from Products.CMFPlone.utils import IndexIterator
    allow_class(IndexIterator)

    # Make IndexIterator available at module level
    this_module.IndexIterator = IndexIterator

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

    # Make listPolicies importable TTW
    ModuleSecurityInfo('Products.CMFPlone.Portal').declarePublic('listPolicies')

    # Make Unauthorized importable TTW
    ModuleSecurityInfo('AccessControl').declarePublic('Unauthorized')

    # Make ConflictError importable TTW
    ModuleSecurityInfo('ZODB.POSException').declarePublic('ConflictError')

    # Make ZCTextIndex ParseError importable TTW
    ModuleSecurityInfo('Products.ZCTextIndex.ParseTree').declarePublic('ParseError')

    # Make DateTimeError importable TTW
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

    # Setup migrations
    import migrations
    migrations.executeMigrations()
    migrations.registerMigrations()

    # Inititalize configuration machinery
    import setup

    # Apply monkey patches
    import patches

    # Register unicode splitter w/ ZCTextIndex
    # pipeline registry
    import UnicodeSplitter

    # Register Plone skins directory
    from Products.CMFCore import DirectoryView
    DirectoryView.registerDirectory('skins', cmfplone_globals)

    # Plone content

    # LargePloneFolder is deprectated and will be removed in Plone 4.0.
    # Usage of PloneFolder is discouraged.
    import PloneFolder, LargePloneFolder
    import Portal

    contentClasses      = ( PloneFolder.PloneFolder,
                            LargePloneFolder.LargePloneFolder, )
    contentConstructors = ( PloneFolder.addPloneFolder,
                            LargePloneFolder.addLargePloneFolder, )

    # CMFCore and CMFDefault tools
    from Products.CMFCore import CachingPolicyManager

    # Plone tools
    import PloneTool, FactoryTool
    import InterfaceTool, MigrationTool, PloneControlPanel
    import MembershipTool, WorkflowTool, URLTool, MetadataTool
    import RegistrationTool, MemberDataTool, SyndicationTool
    import PropertiesTool, ActionsTool, TypesTool, UndoTool
    import CatalogTool, SkinsTool, DiscussionTool
    import CalendarTool, ActionIconsTool, QuickInstallerTool
    import GroupDataTool, GroupsTool
    import TranslationServiceTool

    tools = ( MembershipTool.MembershipTool,
              MemberDataTool.MemberDataTool,
              PloneTool.PloneTool,
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
              GroupsTool.GroupsTool,
              GroupDataTool.GroupDataTool,
              TranslationServiceTool.TranslationServiceTool,
            )

    from Products.CMFCore.utils import ContentInit
    from Products.CMFPlone.utils import ToolInit

    # Register tools and content
    ToolInit('Plone Tool'
             , tools=tools
             , icon='tool.gif'
             ).initialize( context )

    ContentInit('Plone Content'
                , content_types=contentClasses
                , permission=ADD_CONTENT_PERMISSION
                , extra_constructors=contentConstructors
                ).initialize( context )

    import factory
    context.registerClass(Portal.PloneSite,
                          constructors=(factory.addPloneSiteForm,
                                        factory.addPloneSite),
                          icon='skins/plone_images/logoIcon.gif')

# Import "PloneMessageFactory as _" to create messages in the plone domain
from zope.i18nmessageid import MessageFactory
PloneMessageFactory = MessageFactory('plone')

# Import PloneLocalesMessageFactory to create messages in the plonelocales domain
from zope.i18nmessageid import MessageFactory
PloneLocalesMessageFactory = MessageFactory('plonelocales')

# A module alias for the stupidly named plone.py - now called 'ploneview.py'
# 
# If you get weird import errors like "Cannot import module 'utils'" (when 
# trying to import Products.CMFPlone.utils, comment out the next two lines -
# they may be masking the error.
from browser import ploneview
sys.modules['Products.CMFPlone.browser.plone'] = ploneview
