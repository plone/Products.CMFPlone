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
from copy import deepcopy

class FormulatorTool (UniqueObject, SimpleItem):
    """Provides helper methods for doing form validation in Plone using Formulator"""
    id = 'portal_form_validation'
    meta_type= 'CMF Formulator Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    
    security.declarePublic('log')
    def log(self, msg):
        """ """
        import sys
        sys.stdout.write(str(msg))

    security.declarePublic('validate')
    def validate(self, context, validator=None):
        """Convenience method for form handlers.  Calls an optional external validator,
           checks for ID collisions when objects are renamed, then sets up the REQUEST.
           Returns errors in a dictionary.
        """
        # validate is a convenience method that is typically called by a form handling
        # script, e.g. a myobject_edit.py external method in skins/plone_scripts/form_scripts.
        #
        # validate first calls the validation script specified by validator.  Next, it
        # does a basic check on the id parameter: if the id has changed, it makes sure there
        # isn't aready an object with the new id in the current object's container.  Finally,
        # it sets up the REQUEST by calling validate_setupRequest.
        #
        # *** Form handlers should always call validate even if they require no additional
        # validation to check for id collisions and to set up the REQUEST ***
        errors = {}
        if validator != None:
            errors = apply(getattr(context, validator), ())
        context.validate_setupRequest(errors)
        return errors

    security.declarePublic('createForm') # ( CMFCorePermissions.AddPortalContent, 'createForm' )
    def createForm(self):
        """Returns a CMFForm object"""
        # CMFForm wraps Formulator.BasicForm and provides some convenience methods that
        # make BasicForms easier to work with from external methods.
        portalRootObject=getToolByName(self, 'portal_url').getPortalObject()
        form = CMFForm()
        return form.__of__(portalRootObject)

    def manage_afterAdd(self, item, container):
        # self._v_validators is a cache for storing validators so that
        # you don't have to construct and destroy a validator object
        # every time you do a form validation if doing so is expensive.
        # The object is volatile and hence not persisted when Zope is
        # shut down to avoid debugging headaches with persisted objects.
        self._v_validators = {}

    security.declarePublic('cacheValidator')
    def cacheValidator(self, key, validator):
        """Cache a validator for later use"""
        self._v_validators[key] = validator

    security.declarePublic('getValidator')
    def getValidator(self, key):
        """Get a validator from the cache"""
        try:
            return self._v_validators[key]
        except:
            return None

InitializeClass(FormulatorTool)

class CMFForm(BasicForm):
    """Wraps Formulator.BasicForm and provides some convenience methods that
       make BasicForms easier to work with from external methods."""
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    
    security.declarePublic('addField')
    def addField(self, field_id, fieldType, group=None, **kwargs):
        """
        Adds a Formulator Field to the wrapped BasicForm.

        fieldType: An abbreviation for the Field type.
            'String' generates a StringField, 'Int' generates an IntField, etc.
            Uses a StringField if no suitable Field type is found.
        field_id: Name of the variable in question.  Note that Formulator adds
            'field_' to variable names, so you will need to refer to the variable
            foo as field_foo in form page templates.
        group: Formulator group for the field.
        
        Additional arguments: addField passes all other arguments on to the
            new Field object.  In addition, it allows you to modify the
            Field's error messages by passing in arguments of the form
            name_of_message = 'New error message'
                
        See Formulator.StandardFields for details.
        """

        if fieldType[-5:]!='Field':
            fieldType = fieldType+'Field'      

        formulatorFieldClass = None

        if hasattr(StandardFields, fieldType):
            formulatorFieldClass = getattr(StandardFields, fieldType)
        else:
            formulatorFieldClass = getattr(StandardFields, 'StringField')

        # pass a title parameter to the Field
        kwargs['title'] = field_id

        fieldObject = apply(formulatorFieldClass, (field_id, ), kwargs)
        fieldObject = fieldObject.__of__(self)

        # alter Field error messages
        # Note: This messes with Formulator innards and may break in the future.
        # Unfortunately, Formulator doesn't do this already in Field.__init__
        # and there isn't a Python-oriented method for altering message values
        # so at present it's the only option.
        for arg in kwargs.keys():
            if fieldObject.message_values.has_key(arg):
                fieldObject.message_values[arg] = kwargs[arg]

        # Add the new Field to the wrapped BasicForm object
        BasicForm.add_field(self, fieldObject, group)

    security.declarePublic('validate') #security.declareProtected( CMFCorePermissions.AddPortalContent, 'validate' )
    def validate(self, REQUEST):
        """
        Executes the validator for each field in the wrapped BasicForm.add_field
        Returns the results in a dictionary.
        """
        errors={}

        # This is a bit of a hack to make some of Formulator's quirks
        # transparent to developers.  Formulator expects form fields to be
        # prefixed by 'field_' in the request.  To remove this restriction,
        # we mangle the REQUEST, renaming keys from key to 'field_' + key
        # before handing off to Formulator's validators.  We will undo the
        # mangling afterwards.
        for field in self.get_fields():
            key = field.id
            value = REQUEST.get(key)
            if value:
                # get rid of the old key
                try:
                    del REQUEST[key]
                except:
                    pass
                # move the old value to 'field_' + key
                # if there is already a value at 'field_' + key,
                #    move it to 'field_field_' + key, and repeat
                #    to prevent key collisions
                newKey = 'field_' + key
                newValue = REQUEST.get(newKey)
                while newValue:
                    REQUEST[newKey] = value
                    newKey = 'field_' + newKey
                    value = newValue
                    newValue = REQUEST.get(newKey)
                REQUEST[newKey] = value

        try:
            result=self.validate_all(REQUEST)
        except FormValidationError, e:
            for error in e.errors:
                errors[error.field.get_value('title')]=error.error_text

        # unmangle the REQUEST
        for field in self.get_fields():
            key = field.id
            value = 1
            while value:
                key = 'field_' + key
                value = REQUEST.get(key)
                if value:
                    REQUEST[key[6:]] = value
                    try:
                        del REQUEST[key]
                    except:
                        pass

        return errors

InitializeClass(CMFForm)