from Products.Formulator.StandardFields import StringField, EmailField
from Products.Formulator.Form import FormValidationError, BasicForm
from Products.Formulator import StandardFields

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions

def log(msg):
    import sys
    sys.stdout.write(msg)

class FormulatorTool (UniqueObject, SimpleItem):
    """ encapsulates the ways forms should and can work inside a CMF """
    id = 'portal_form_validation'
    meta_type= 'CMF Formulator Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
                           
    security.declarePublic('createForm') # ( CMFCorePermissions.AddPortalContent, 'createForm' )
    def createForm(self):
        """ returns a BasicForm object """
        portalRootObject=getToolByName(self, 'portal_url').getPortalObject()
        form=CMFForm()
        return form.__of__(portalRootObject)

    security.declarePublic('createField') # security.declareProtected( CMFCorePermissions.AddPortalContent, 'createField' )
    def createField(self, fieldType, field_id, **kwargs):
        """ returns a Field class definition, if it can not find one a StringField is returned """
        formulatorFieldClass = None

        if fieldType[-5:]!='Field':
            fieldType = fieldType+'Field'      

        if hasattr(StandardFields, fieldType):
            formulatorFieldClass = getattr(StandardFields, fieldType)
        else:
            formulatorFieldClass = getattr(StandardFields, 'StringField')
        
        fieldObject = apply(formulatorFieldClass, (field_id, ), kwargs)
        return fieldObject.__of__(self)

    security.declarePublic('validate') #security.declareProtected( CMFCorePermissions.AddPortalContent, 'validate' )
    def validate(self, form):
        """ given a CMFForm object populated with Fields will validate it,
            returns validation errors or None if no errors
        """
        errors={}
        try:
            result=form.validate_all(self.REQUEST)
        except FormValidationError, e:
            for error in e.errors:
                errors[error.field.get_value('title')]=error.error_text     
            return errors

InitializeClass(FormulatorTool)

class CMFForm(BasicForm):
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    
    security.declarePublic('add_field')
    def add_field(self, field, group=None):
        BasicForm.add_field(self, field, group)

InitializeClass(CMFForm)
