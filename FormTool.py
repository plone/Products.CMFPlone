from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from OFS.Traversable import Traversable
from Acquisition import aq_parent, aq_base
from FormulatorTool import CMFForm
from FactoryTool import PendingCreate
from OFS.SimpleItem import Item
from OFS.ObjectManager import bad_id


validator_cache = {}  # a place to stash cached validators
# (we don't want to persist them in the ZODB since that would make debugging a big pain)

debug = 0  # enable/disable logging

class FormTool(UniqueObject, SimpleItem):
    id = 'portal_form'
    meta_type= 'Plone Form Tool'
    security = ClassSecurityInfo()

    # special-purpose items used in the REQUEST
    error_key = 'errors'                    # a dictionary used for storing form validation errors
    form_submitted_key = 'form_submitted'   # supplies the name of the form submitted
    id_key = 'id'                           # the id for the object being operated on (can be None)
    id_error_key = 'id_error'


    def setValidator(self, form, validator):
        """Register a form validator"""
        property_tool = getattr(self, 'portal_properties')
        formprops = getattr(property_tool, 'form_properties')
        if formprops.hasProperty(form):
            form_props._updateProperty(form, validator)
        else:
            formprops._setProperty(form, validator)


    security.declarePublic('getValidator')
    def getValidator(self, form):
        """Get the validator registered for a given form"""
        property_tool = getattr(self, 'portal_properties')
        form_props = getattr(property_tool, 'form_properties')
        validator = form_props.getProperty(form, None)
        if validator:
            validator = validator.strip()
        return validator


    security.declarePublic('validate')
    def validate(self, context, REQUEST, validator=None):
        """Convenience method for form handlers.  Calls an optional external validator,
           checks for ID collisions when objects are renamed, then sets up the REQUEST.
           Places a dictionary of errors in the REQUEST that is accessed via REQUEST[FormTool.error_key]
           Returns a status of 'success' or 'failure'.
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
        if validator and validator.strip() != '':
            errors = apply(getattr(context, validator), ())
            # make sure errors is a dictionary
            if not type(errors) == type({}):
                errors = {}

        messages = context.errorMessages()
        # do some basic id validation
        id = REQUEST.get(self.id_key, None)
        if id:
            if bad_id(id):
                # id is bad
                errors[self.id_key] = messages['illegal_id']
            else:
                # id is good; make sure we have no id collisions

                if self._isPendingCreate(context):
                    # always check for collisions if we are creating a new object
                    checkForCollision = 1
                else:
                    # if we have an existing object, only check for collisions if we are changing the id
                    checkForCollision = (context.getId() != id)

                # perform the actual check
                if checkForCollision:
                    container = context.getParentNode()
                    if id in container.objectIds():
                        errors[self.id_key] = messages['id_exists']

        # set a status message indicating errors
        if errors:
            self.REQUEST.set('portal_status_message', messages['error_exists'])

        self.REQUEST.set(self.error_key, errors)
        if errors:
            return 'failure'
        else:
            return 'success'


    security.declarePublic('createForm')
    def createForm(self):
        """Returns a CMFForm object"""
        # CMFForm wraps Formulator.BasicForm and provides some convenience methods that
        # make BasicForms easier to work with from external methods.
        portalRootObject=getToolByName(self, 'portal_url').getPortalObject()
        form = CMFForm()
        return form.__of__(portalRootObject)


    security.declarePublic('cacheValidator')
    def cacheValidator(self, key, validator):
        """Cache a validator for later use"""
        global validator_cache
        validator_cache[key] = validator


    security.declarePublic('getValidator')
    def getCachedValidator(self, key):
        """Get a validator from the cache"""
        global validator_cache
        return validator_cache.get(key, None)


    def __bobo_traverse__(self, REQUEST, name):
        # We intercept traversal when a form needs validation.  We insert a FormValidator object
        # into the traversal stack which, when published, does the proper validation and then
        # hands off to the navigation tool to determine the correct object to publish.

        # see if we are handling validation for this form
        validator = self.getValidator(name)
        if not validator:
            # no -- do normal traversal
            target = getattr(aq_parent(self), name, None)
            if name.endswith('.js'):
                self.log('name: %s, target: <Javascript>, context: %s' % (name, str(aq_parent(self))), '_traverseTo')
            else:
                self.log('name: %s, target: %s, context: %s' % (name, target, str(aq_parent(self))), '_traverseTo')
            if target:
                return target
            else:
                return REQUEST.RESPONSE.notFoundError("%s\n" % (name))

        # There are three potential points of entry to a form:
        # 1) The form is accessed directly from a URL, e.g. http://plone/portal_form/link_edit:
        #       In this case we have REQUEST.errors = None, REQUEST.form_submitted = None
        # 2) The form is filled out and submitted.
        #       In this case we have REQUEST.errors = None, REQUEST.form_submitted = 1
        # 3) A form validation error occurs, and the form is invoked by the navigation tool
        #       In this case we have REQUEST.errors != None, REQUEST.form_submitted = 1
        #
        # We only need to invoke the validator for case (2)

        # see if we need to invoke validation
        errors = REQUEST.get(self.error_key, None)
        # Make sure errors is something generated by us, not something submitted via POST or GET
        if not type(errors) != type({}):
            errors = None
        form_submitted = REQUEST.get(FormTool.form_submitted_key, None)
        self.log('errors = '+str(errors) + ', form_submitted = ' + str(form_submitted), '__bobo_traverse__')

        # We wrap the object in the acquisition layer of the parent of the FormTool
        # so that subsequent forms will operate on the FormTool's context and not
        # on the FormTool.
        do_validate = form_submitted and not errors
        self.log('returning FormValidator(%s,%s,%s)' % (name, validator, do_validate), '__bobo_traverse__')
        self.log(REQUEST.URL)
        return FormValidator(name, validator, do_validate).__of__(aq_parent(self)) # wrap in acquisition layer


    def _isPendingCreate(self, obj):
        return obj.__class__ == PendingCreate

  
    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
        prefix = 'FormTool'
        if loc:
            prefix = prefix + '. ' + str(loc)
        sys.stdout.write(prefix+': '+str(msg)+'\n')

InitializeClass(FormTool)


class FormValidator(SimpleItem):
    """ """
    # When a form needs validation, we publish a FormValidator object in place of the next form.
    # The FormValidator calls a validator method on the variables in the REQUEST and then
    # hands off to a page determined by the NavigationTool
    security = ClassSecurityInfo()

    def __init__(self, form, validator, do_validate):
        self.form = form
        self.validator = validator
        self.do_validate = do_validate


    security.declarePublic('__call__')
    def __call__(self, REQUEST, **kw):
        """ """
        self.log('validator[%s] = \'%s\'' % (self.form, self.validator), '__call__')

        if self.do_validate:
            context = self.aq_parent
            form_tool = context.portal_form
            self.log('invoking validation, status = '+str(form_tool.validate(context, REQUEST, self.validator)))
            # invoke validation
            status = form_tool.validate(context, REQUEST, self.validator)

            # check for validation errors
            if status == 'success':
                # if no errors, create a new object if creation is pending and change the context
                if context.__class__ == PendingCreate:
                    self.log("new id = " + REQUEST[FormTool.id_key])
                    context = context.invokeFactory(REQUEST[FormTool.id_key], )

            return context.portal_navigation.getNext(context, self.form, status, **kw)
        else:
            self.log('going to %s.%s' % (str(aq_parent(self)), self.form))
            target = getattr(aq_parent(self), self.form, None)
            return target(REQUEST, **kw)


    index_html = None  # call __call__, not index_html


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
        prefix = 'FormValidator'
        if loc:
            prefix = prefix + '. ' + str(loc)
        sys.stdout.write(prefix+': '+str(msg)+'\n')

InitializeClass(FormValidator)
