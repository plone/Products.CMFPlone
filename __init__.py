from Products.CMFCore import DirectoryView, utils
from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
import MembershipTool, FormulatorTool, CalendarTool
import PloneFolder

BROWSE_DIRECTORY_LISTING = 'Browse directory listing'
ADD_CONTENT_PERMISSION = 'Add portal content'

#for plone_debug method
import zLOG
ModuleSecurityInfo('zLOG').declarePublic('LOG')
ModuleSecurityInfo('zLOG').declarePublic('INFO')

#for form validation bits
from AccessControl import ModuleSecurityInfo
def allow_class(Class): 
    """Allow a class and all of its methods to be used from a 
    restricted Script. The argument Class must be a class.""" 
    Class._security = sec = ClassSecurityInfo() 
    sec.declareObjectPublic() 
    sec.setDefaultAccess(1) 
    sec.apply(Class) 
    from Globals import InitializeClass 
    InitializeClass(Class)

#allow_class(ColorPreset)

ModuleSecurityInfo('Products.Formulator').declarePublic('StringField','EmailField')
ModuleSecurityInfo('Products.Formulator.Form').declarePublic('FormValidationError', 'BasicForm')

from Products.Formulator.StandardFields import StringField, EmailField
from Products.Formulator.Form import FormValidationError, BasicForm
allow_class(StringField)
allow_class(EmailField)
allow_class(FormValidationError)
allow_class(BasicForm)

try: from Products.CMFDecor import FSPageTemplate
except: from Products.CMFCore import FSPageTemplate

tools = ( MembershipTool.MembershipTool
        , FormulatorTool.FormulatorTool 
        , CalendarTool.CalendarTool )

contentClasses = ( PloneFolder.PloneFolder , )
contentConstructors = ( PloneFolder.addPloneFolder, )

DirectoryView.registerDirectory('skins', globals())
cmfplone_globals=globals()

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

