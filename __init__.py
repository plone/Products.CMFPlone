import sys
import os
import Globals

cmfplone_globals = globals()
this_module = sys.modules[ __name__ ]
_marker = []

# Stores the available 'Customization Policies'
custom_policies = {}

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

    # zLOG is deprecated in Zope > 2.7.0, use logger instead
    ModuleSecurityInfo('logging').declarePublic('getLogger')
    from logging import Logger
    allow_class(Logger)

    ModuleSecurityInfo('zLOG').declarePublic('LOG')
    ModuleSecurityInfo('zLOG').declarePublic('INFO')
    ModuleSecurityInfo('zLOG').declarePublic('WARNING')

    allow_module('Products.CMFPlone.utils')

    # This is now deprecated, use utils instead.
    allow_module('Products.CMFPlone.PloneUtilities')

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

    # Backward compatibility only, please import from utils directly
    from Products.CMFPlone.utils import transaction_note, base_hasattr
    this_module.transaction_note = transaction_note
    this_module.base_hasattr = base_hasattr

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
    import PloneContent, PloneFolder, PloneWorkflow, FolderWorkflow
    import Portal

    contentClasses = ( PloneFolder.PloneFolder , )
    contentConstructors = ( PloneFolder.addPloneFolder, )
    ftis = ( PloneFolder.factory_type_information,
             Portal.factory_type_information, )

    try:
        import LargePloneFolder
    except ImportError:
        pass
    else:
        contentClasses += ( LargePloneFolder.LargePloneFolder, )
        contentConstructors += ( LargePloneFolder.addLargePloneFolder,)
        ftis += (LargePloneFolder.factory_type_information, )

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

    from Products.CMFCore.utils import initializeBasesPhase1
    from Products.CMFCore.utils import initializeBasesPhase2
    from Products.CMFCore.utils import ContentInit
    from Products.CMFPlone.utils import ToolInit

    # Register tools, content, and customization policies
    z_bases = initializeBasesPhase1(contentClasses, this_module)
    initializeBasesPhase2(z_bases, context)

    ToolInit('Plone Tool'
             , tools=tools
             , product_name='CMFPlone'
             , icon='tool.gif'
             ).initialize( context )

    ContentInit('Plone Content'
                , content_types=contentClasses
                , permission=ADD_CONTENT_PERMISSION
                , extra_constructors=contentConstructors
                , fti=ftis
                ).initialize( context )

    Portal.register(context, cmfplone_globals)

    import CustomizationPolicy
    CustomizationPolicy.register(context, cmfplone_globals)

    ModuleSecurityInfo('Products.CMFPlone').declarePrivate('transaction')

# Provide backward compatibility for products relying on this import location
# BBB: Remove in Plone 2.3
import transaction
