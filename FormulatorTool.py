from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from OFS.ObjectManager import bad_id
from PloneUtilities import log_deprecated
from copy import deepcopy
import sys

class FormulatorTool (UniqueObject, SimpleItem):
    """Provides helper methods for doing form validation in Plone using Formulator"""
    id = 'portal_form_validation'
    meta_type= 'CMF Formulator Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    
    security.declarePublic('log')
    def log(self, msg):
        """ """
        log_deprecated(msg)

    # DEPRECATED
    security.declarePublic('validate')
    def validate(self, context, validator=None):
        """Convenience method for form handlers.  Calls an optional external validator,
           checks for ID collisions when objects are renamed, then sets up the REQUEST.
           Returns errors in a dictionary.
        """
        log_deprecated('FormulatorTool.validate has been deprecated\n')
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

        portal_form = getToolByName(self, 'portal_form')
        REQUEST = context.REQUEST
        
        errors = {}
        if validator and validator.strip() != '':
            errors = apply(getattr(context, validator), ())
            # make sure errors is a dictionary
            if not type(errors) == type({}):
                errors = {}

        messages = context.errorMessages()
        # do some basic id validation
        id = REQUEST.get('id', None)
        if id:
            if not portal_form.good_id(id):
                # id is bad
                errors['id'] = messages['illegal_id']
            else:
                # perform the actual check
                if context.getId() != id:
                    container = context.getParentNode()
                    if id in container.objectIds():
                        errors['id'] = messages['id_exists']

        # set a status message indicating errors
        if errors:
            self.REQUEST.set('errors', errors)
            self.REQUEST.set('portal_status_message', messages['error_exists'])
        return errors


    # DEPRECATED
    security.declarePublic('createForm') # ( CMFCorePermissions.AddPortalContent, 'createForm' )
    def createForm(self):
        """Returns a CMFForm object"""
        log_deprecated('FormulatorTool.createForm has been deprecated\n')
        # CMFForm wraps Formulator.BasicForm and provides some convenience methods that
        # make BasicForms easier to work with from external methods.
        return getToolByName(self, 'portal_form').createForm()

    # DEPRECATED
    security.declarePublic('cacheValidator')
    def cacheValidator(self, key, validator):
        """Cache a validator for later use"""
        log_deprecated('FormulatorTool.cacheValidator has been deprecated\n')
        return getToolByName(self, 'portal_form').cacheValidator(key, validator)

    # DEPRECATED
    security.declarePublic('getValidator')
    def getValidator(self, key):
        """Get a validator from the cache"""
        log_deprecated('FormulatorTool.getValidator has been deprecated\n')
        return getToolByName(self, 'portal_form').getCachedValidator(key)

InitializeClass(FormulatorTool)
