# $Id: FormTool.py,v 1.28.4.10 2004/04/16 17:12:48 limi Exp $

from Products.Formulator.Form import FormValidationError, BasicForm
from Products.Formulator import StandardFields
from Products.CMFCore.utils import UniqueObject
from Products.CMFFormController.ValidationError import ValidationError
from Products.CMFFormController.ControllerState import ControllerState
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from OFS.Traversable import Traversable
from Acquisition import aq_parent, aq_base
from OFS.SimpleItem import Item
from OFS.ObjectManager import bad_id
from ZPublisher.mapply import mapply
from ZPublisher.Publish import call_object, missing_name, dont_publish_class
from Products.CMFCore.utils import getToolByName
from PloneUtilities import log_deprecated
from interfaces.FormTool import IFormTool, ICMFForm
from PloneUtilities import log as debug_log
from NavigationTool import ScriptStatus
from ZODB.POSException import ConflictError
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

validator_cache = {}  # a place to stash cached validators

# (we don't want to persist them in the ZODB since that would make
# debugging a big pain)

debug = 0  # enable/disable logging

class FormTool(PloneBaseTool, UniqueObject, SimpleItem):
    id = 'portal_form'
    meta_type= 'Plone Form Tool'
    toolicon = 'skins/plone_images/error_icon.gif'
    security = ClassSecurityInfo()
    
    __implements__ = (PloneBaseTool.__implements__, IFormTool, 
                      SimpleItem.__implements__, )

    # special-purpose items used in the REQUEST
    # a dictionary used for storing form validation errors
    error_key = 'errors'
    # supplies the name of the form submitted
    form_submitted_key = 'form_submitted'
    # the id for the object being operated on (can be None)
    id_key = 'id'

    validation_status_key = 'validation_status'


    def __before_publishing_traverse__(self, other, REQUEST):

        # kill off everything in the traversal stack after the item
        # after portal_form

        stack = REQUEST.get('TraversalRequestNameStack', [])
        # self.log('stack = ' + str(stack))
        # get rid of extra portal_forms
        if stack:
            while 'portal_form' in stack:
                stack.remove('portal_form')
            REQUEST.set('TraversalRequestNameStack', [stack[-1]])


    def setValidators(self, form, validators=None):
        """Register a chain of validators for a form"""
        if validators is None:
            validators = ['validate_id']
        if type(validators) != type([]):
            validators = [validators]
        property_tool = getattr(self, 'portal_properties')
        formprops = getattr(property_tool, 'form_properties')

        st = ','.join(validators)
        if formprops.hasProperty(form):
            formprops._updateProperty(form, st)
        else:
            formprops._setProperty(form, st)


    def getValidators(self, form):
        """Get the chain of validators registered for a given form"""
        property_tool = getattr(self, 'portal_properties')
        form_props = getattr(property_tool, 'form_properties')
        validators = form_props.getProperty(form, None)
        if validators is None:
            return None
        validators = validators.strip()
        if validators == '':
            return []
        return validators.split(',')


    def createForm(self):
        """Returns a CMFForm object"""
        # CMFForm wraps Formulator.BasicForm and provides some
        # convenience methods that make BasicForms easier to work with
        # from external methods.

        form = CMFForm()
        return form.__of__(self)


    def cacheValidator(self, key, validator):
        """Cache a validator for later use"""
        global validator_cache
        validator_cache[key] = validator


    def getCachedValidator(self, key):
        """Get a validator from the cache"""
        global validator_cache
        return validator_cache.get(key, None)


    def __bobo_traverse__(self, REQUEST, name):
        # self.log('in bobo_traverse (%s)' % name)
        # We intercept traversal when a form needs validation.  We
        # insert a FormValidator object into the traversal stack
        # which, when published, does the proper validation and then
        # hands off to the navigation tool to determine the correct
        # object to publish.

        # see if we are handling validation for this form
        validators = self.getValidators(name)

        REQUEST = self.REQUEST

        # self.log('validators = ' + str(validators))
        if validators is None:

            # make sure this is a normal REQUEST
            if hasattr(REQUEST, 'RESPONSE'):
                parent = aq_parent(self)
                # no -- do normal traversal
                parent = aq_parent(self)
                if hasattr(parent, '__bobo_traverse__'):
                    return parent.__bobo_traverse__(REQUEST, name)
                if hasattr(parent, name):
                    return getattr(parent, name)
                try:
                    return parent[name]
                except (KeyError, AttributeError):
                    pass
                return REQUEST.RESPONSE.notFoundError(name)
            # no, this is a fake request issued by unrestrictedTraverse
            else:
                if hasattr(self, name):
                    return getattr(self, name)
                try:
                    return self[name]
                except (KeyError, AttributeError):
                    pass
                raise KeyError, name


        # There are three potential points of entry to a form:

        # 1) The form is accessed directly from a URL,
        #       e.g. http://plone/portal_form/link_edit: In this case
        #       we have REQUEST.errors = None, REQUEST.form_submitted
        #       = None

        # 2) The form is filled out and submitted.  In this case we
        # have REQUEST.errors = None, REQUEST.form_submitted = 1

        # 3) A form validation error occurs, and the form is invoked
        # by the navigation tool In this case we have REQUEST.errors
        # != None, REQUEST.form_submitted = 1
        #
        # We only need to invoke the validators for case (2)


        # see if we need to invoke validation
        errors = REQUEST.get(self.error_key, None)
        # Make sure errors is something generated by us, not something
        # submitted via POST or GET

        if not type(errors) != type({}):
            errors = None
        form_submitted = REQUEST.get(FormTool.form_submitted_key, None)

        # We wrap the object in the acquisition layer of the parent of
        # the FormTool so that subsequent forms will operate on the
        # FormTool's context and not on the FormTool.
        do_validate = form_submitted and not errors

        if not do_validate:
            # no need for validation -- do normal traversal
            target = getattr(aq_parent(self), name, None)
            if target:
                return target
            else:
                return REQUEST.RESPONSE.notFoundError("%s\n" % (name))

            # self.log('returning validator')
        validator = FormValidator(name, validators, aq_parent(self))
        return validator.__of__(aq_parent(self)) # wrap in acquisition layer


    # DEPRECATED
    def setValidator(self, form, validator):
        """Register a form validator"""
        log_deprecated('setValidator has been marked for deprecation.  Please use setValidators instead.')
        return self.setValidators(form, [validator, 'validate_id'])

    # DEPRECATED
    security.declarePublic('getValidator')
    def getValidator(self, form):
        """Get the validator registered for a given form"""
        log_deprecated('getValidator has been marked for deprecation.  Please use getValidators instead.')
        return self.getValidators(form)[0]

    # DEPRECATED
    def good_id(self, id):
        log_deprecated('good_id has been marked for deprecation.  Please use plone_utils.good_id instead.')
        m = bad_id(id)
        if m is not None:
            return 0
        return 1


    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        prefix = 'FormTool'
        if loc:
            prefix = prefix + '. ' + str(loc)
        debug_log(prefix+': '+str(msg))

InitializeClass(FormTool)


class FormValidator(SimpleItem):
    """ """
    # When a form needs validation, we publish a FormValidator object
    # in place of the next form.  The FormValidator calls a validator
    # method on the variables in the REQUEST and then hands off to a
    # page determined by the NavigationTool

    security = ClassSecurityInfo()

    def __init__(self, form, validators, context):
        self.form = form
        self.validators = validators
        self.id = "Error" # This should only be seen if an error occurs
        self.title = None
        # self.log("created validator")

    def __str__(self):
        return 'FormValidator, form=%s, validators=%s' % \
               (self.form, str(self.validators))


    security.declarePublic('__call__')
    def __call__(self, client=None, REQUEST={}, RESPONSE=None, **kw):
        """ """
        trace = []

        try:
            trace.append('Invoking validation')
            context = aq_parent(self)
            # invoke validation

            (status, kwargs, trace) = self._validate(context, self.REQUEST, trace)

            (obj, kwargs) = context.portal_navigation.getNextObject(context, self.form, status, trace, **kwargs)
            kwargs['REQUEST'] = self.REQUEST

            # Set the FormValidator's id and title to those of the
            # published object so that breadcrumbs can extract an id
            # and title from the traversal stack.

            if obj:
                self.id = getattr(obj, 'id', None)
                self.title = getattr(obj, 'title', None)
            return apply(obj, (), kwargs)

        except ConflictError:
            raise
        except:
            nav = getToolByName(self, 'portal_navigation')
            nav.logTrace(trace)
            raise


    index_html = None  # call __call__, not index_html


    def _validate(self, context, REQUEST, trace):
        """Execute validators on the validation stack then sets up the REQUEST and returns a status.
           Places a dictionary of errors in the REQUEST that is accessed via REQUEST[FormTool.error_key]
        """
        try:
            errors = {}
            # default return value if the validator list is empty
            status = 'success'
            kwargs = {}
            for validator in self.validators:
                trace.append('Invoking %s' % validator)
                v = context.restrictedTraverse(validator, default=None)
                if v is None:
                    raise KeyError("Unable to find validator '%s' in context '%s'.  Check your skins path." % (validator, str(context)))

                # handle CMFFormController validators properly
                if getattr(v, 'is_validator', 0):
                    # get a controller_state object and populate it
                    form_controller = getToolByName(context, 'portal_form_controller')
                    try:
                        controller_state = form_controller.getState(context, 1)
                    except ValueError:
                        controller_state = ControllerState()
                        controller_state.set(context=context)
                        controller_state.setButton(None)
                        for k in REQUEST.keys():
                            if k.startswith('form.button.'):
                                controller_state.setButton(k[len('form.button.'):])
                                break
                    controller_state.setStatus(REQUEST.get('validation_status', 'success'))
                    controller_state.setErrors(REQUEST.get('errors', {}))
                    # XXX this is a bit of a hack -- lots of REQUEST keys could be
                    # controller_state kwargs, but we don't know which ones.
                    # portal_status_message is a common one.
                    msg = REQUEST.get('portal_status_message', None)
                    if msg:
                        controller_state.setKwargs({'portal_status_message':msg})
                    REQUEST.set('controller_state', controller_state)
                    if controller_state.hasValidated(validator):
                        continue
                    try:
                        controller_state = mapply(v, REQUEST.args, REQUEST,
                                                  call_object, 1, missing_name, dont_publish_class,
                                                  REQUEST, bind=1)
                        controller_state._addValidator(validator)
                    except ValidationError, e:
                        # if a validator raises a ValidatorException, execution of
                        # validators is halted and the controller_state is set to
                        # the controller_state embedded in the exception
                        controller_state = e.controller_state
                        state_class = getattr(controller_state, '__class__', None)
                        if state_class != ControllerState:
                            raise Exception, 'Bad ValidationError state (type = %s)' % str(state_class)
                        status = controller_state.getStatus()
                        kwargs = controller_state.getKwargs()
                        kwargs['errors'] = controller_state.getErrors()
                        new_context = controller_state.getContext()
                        break
                    state_class = getattr(controller_state, '__class__', None)
                    if state_class != ControllerState:
                        raise Exception, 'Bad validator return type from validator %s (%s)' % (str(v), str(state_class))

                    status = controller_state.getStatus()
                    kwargs = controller_state.getKwargs()
                    kwargs['errors'] = controller_state.getErrors()
                    new_context = controller_state.getContext()

                else:
                    script_status = mapply(v, REQUEST.args, REQUEST,
                                           call_object, 1, missing_name, dont_publish_class,
                                           REQUEST, bind=1)

                    # The preferred return type for scripts will
                    # eventually be an object.  Until then, preserve
                    # compatibility with 1.0 alpha 4

                    if type(script_status) == type(()):
                        (status, errors, kwargs) = script_status
                        kwargs['errors'] = errors
                        script_status = ScriptStatus(status, kwargs, None)

                        # disable deprecation warning for now
                        # log_deprecated('Validator \'%s\' uses a return
                        # signature that has been marked for deprecation.
                        # Validators should return a ScriptStatus object.'
                        # % validator)

                    status = script_status.status
                    kwargs = script_status.kwargs
                    new_context = script_status.new_context

                self.REQUEST.set('validation_status', status)
                for key in kwargs.keys():
                    self.REQUEST.set(key, kwargs[key])
                trace.append('\t -> (%s, %s)' % (status, str(kwargs)))
                if new_context is not None:
                    context = new_context
                    trace.append("\t context changed to '%s'" % str(context))
            trace.append('Validation returned (%s, %s)' % (status, str(kwargs)))
            return (status, kwargs, trace)
        except ConflictError:
            raise
        except:
            nav = getToolByName(self, 'portal_navigation')
            nav.logTrace(trace)
            raise


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        prefix = 'FormValidator'
        if loc:
            prefix = prefix + '. ' + str(loc)
        debug_log(prefix+': '+str(msg))

InitializeClass(FormValidator)


class CMFForm(BasicForm):
    """Wraps Formulator.BasicForm and provides some convenience methods that
       make BasicForms easier to work with from external methods."""
    security = ClassSecurityInfo()
    security.declareObjectPublic()
    __implements__ = ICMFForm,

    security.declareProtected('View', 'get_field')
    def get_field(self, id, include_disabled=0):
        """Get a field of a certain id, wrapping in context of self
        """
        return self.fields[id].__of__(self)

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


    security.declarePublic('validate')
    def validate(self, REQUEST, errors=None):
        """
        Executes the validator for each field in the wrapped BasicForm.add_field
        Returns the results in a dictionary.
        """

        if errors is None:
            errors = REQUEST.get('errors', {})

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
                except (KeyError, AttributeError):
                    pass
                # move the old value to 'field_' + key
                # if there is already a value at 'field_' + key,
                #    move it to 'field_field_' + key, and repeat
                #    to prevent key collisions
                newKey = 'field_%s' % key
                newValue = REQUEST.get(newKey)
                while newValue:
                    REQUEST[newKey] = value
                    newKey = 'field_%s' % newKey
                    value = newValue
                    newValue = REQUEST.get(newKey)
                REQUEST[newKey] = value

        try:
            result = self.validate_all(REQUEST)
        except FormValidationError, e:
            result = {}
            for error in e.errors:
                errors[error.field.get_value('title')]=error.error_text

        # unmangle the REQUEST
        for field in self.get_fields():
            key = field.id
            value = 1
            while value:
                key = 'field_%s' % key
                value = result.get(key[6:], None) or REQUEST.get(key)
                if value:
                    REQUEST[key[6:]] = value
                    try:
                        del result[key[6:]]
                    except (KeyError, AttributeError):
                        pass
                    try:
                        del REQUEST[key]
                    except (KeyError, AttributeError):
                        pass

        return errors

InitializeClass(CMFForm)
