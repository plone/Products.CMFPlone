cmfplone_globals=globals()
custom_policies={} #stores the registered Policies

from Products.CMFCore import DirectoryView, utils
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
import MembershipTool, FormulatorTool, TranslatorTool, PloneTool, WorkflowTool
import PloneFolder, Portal
import CustomizationPolicy

ADD_CONTENT_PERMISSION = 'Add portal content'

#for plone_debug method
import zLOG
ModuleSecurityInfo('zLOG').declarePublic('LOG')
ModuleSecurityInfo('zLOG').declarePublic('INFO')
ModuleSecurityInfo('Products.CMFPlone.Portal').declarePublic('listPolicies')

#for form validation bits
def allow_class(Class): 
    """Allow a class and all of its methods to be used from a 
    restricted Script. The argument Class must be a class.""" 
    Class._security = sec = ClassSecurityInfo() 
    sec.declareObjectPublic() 
    sec.setDefaultAccess(1) 
    sec.apply(Class) 
    from Globals import InitializeClass 
    InitializeClass(Class)

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
        , TranslatorTool.TranslatorTool
        , PloneTool.PloneTool
        , WorkflowTool.WorkflowTool )

contentClasses = ( PloneFolder.PloneFolder , )
contentConstructors = ( PloneFolder.addPloneFolder, )

DirectoryView.registerDirectory('skins', globals())

def initialize(context):
    utils.ToolInit('Plone Tool', tools=tools,
                   product_name='CMFPlone', icon='tool.gif',
                   ).initialize( context )
    utils.ContentInit( 'Plone Content'
                     , content_types=contentClasses
                     , permission=ADD_CONTENT_PERMISSION
                     , extra_constructors=contentConstructors
                     , fti=PloneFolder.factory_type_information
                     ).initialize( context )
    Portal.register(context, globals())
    CustomizationPolicy.register(context, globals())
