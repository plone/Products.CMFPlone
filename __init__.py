cmfplone_globals=globals()
custom_policies={} #stores the registered Policies
import migrations
from Products.CMFCore import CachingPolicyManager, DirectoryView, utils
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo, allow_module, allow_class, allow_type
import MembershipTool, FormulatorTool, PloneTool, WorkflowTool
import NavigationTool, FactoryTool, FormTool, PropertiesTool, MigrationTool
import PloneFolder, Portal, PloneWorkflow, FolderWorkflow
import CustomizationPolicy, PrivateSitePolicy

import sys
import StatelessTreeNav
import Globals
from os import path

ADD_CONTENT_PERMISSION = 'Add portal content'

#for plone_debug method
import zLOG
def log(message,summary='',severity=0):
    zLOG.LOG('MyDebugLog',severity,summary,message)

ModuleSecurityInfo('zLOG').declarePublic('LOG')
ModuleSecurityInfo('zLOG').declarePublic('INFO')
ModuleSecurityInfo('Products.CMFPlone.Portal').declarePublic('listPolicies')

# for content_status_modify
from Products.CMFCore.WorkflowCore import ObjectMoved, ObjectDeleted
ModuleSecurityInfo('WorkflowCore').declarePublic('ObjectMoved')
ModuleSecurityInfo('WorkflowCore').declarePublic('ObjectDeleted')
allow_class(ObjectMoved)
allow_class(ObjectDeleted)

#for form validation bits
from PloneUtilities import IndexIterator
allow_class(IndexIterator)

from PloneBatch import Batch
allow_class(Batch)

from StringIO import StringIO
allow_class(StringIO)

ModuleSecurityInfo('Products.Formulator').declarePublic('StringField','EmailField')
ModuleSecurityInfo('Products.Formulator.Form').declarePublic('FormValidationError', 'BasicForm')

from Products.Formulator.StandardFields import StringField, EmailField
from Products.Formulator.Form import FormValidationError, BasicForm
allow_class(StringField)
allow_class(EmailField)
allow_class(FormValidationError)
allow_class(BasicForm)

def transaction_note(note):
    """ write human legible note """
    T=get_transaction()
    T.note(str(note))

ModuleSecurityInfo('Products.CMFPlone').declarePublic('transaction_note')

tools = ( MembershipTool.MembershipTool
        , FormulatorTool.FormulatorTool 
        , PloneTool.PloneTool
        , WorkflowTool.WorkflowTool
        , CachingPolicyManager.CachingPolicyManager
        , NavigationTool.NavigationTool
        , FactoryTool.FactoryTool
        , FormTool.FormTool
        , PropertiesTool.PropertiesTool
        , MigrationTool.MigrationTool )

contentClasses = ( PloneFolder.PloneFolder , )
contentConstructors = ( PloneFolder.addPloneFolder, )

DirectoryView.registerDirectory('skins', cmfplone_globals)
this_module = sys.modules[ __name__ ]
z_bases = utils.initializeBasesPhase1(contentClasses, this_module)

misc_ = {'plone_icon': Globals.ImageFile(path.join('skins','plone_images','logoIcon.gif'), cmfplone_globals)}

def initialize(context):
    utils.initializeBasesPhase2( z_bases, context )    
    utils.ToolInit('Plone Tool', tools=tools,
                   product_name='CMFPlone', icon='tool.gif',
                   ).initialize( context )
    utils.ContentInit( 'Plone Content'
                     , content_types=contentClasses
                     , permission=ADD_CONTENT_PERMISSION
                     , extra_constructors=contentConstructors
                     , fti=PloneFolder.factory_type_information
                     ).initialize( context )
    Portal.register(context, cmfplone_globals)
    CustomizationPolicy.register(context, cmfplone_globals)
    PrivateSitePolicy.register(context, cmfplone_globals)

# setup ZODB if needed
import PloneInitialize

# setup migrations
migrations.registerMigrations()
