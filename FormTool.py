from Products.Formulator.Form import FormValidationError, BasicForm
from Products.Formulator import StandardFields
from Products.CMFCore.utils import UniqueObject
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
from NavigationTool import NavigationError

from PloneUtilities import log as debug_log

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
    validation_status_key = 'validation_status'


    def __before_publishing_traverse__(self, other, REQUEST):
        # kill off everything in the traversal stack after the item after portal_form
        stack = REQUEST.get('TraversalRequestNameStack', None)
        REQUEST.set('TraversalRequestNameStack', [stack[-1]])


    def setValidators(self, form, validators = ['validate_id']):
        """Register a chain of validators for a form"""
        if type(validators) != type([]):
            validators = [validators]
        property_tool = getattr(self, 'portal_properties')
        formprops = getattr(property_tool, 'form_properties')

        st = ','.join(validators)
        if formprops.hasProperty(form):
            form_props._updateProperty(form, st)
        else:
            formprops._setProperty(form, st)


    def getValidators(self, form):
        """Get the chain of validators registered for a given form"""
        property_tool = getattr(self, 'portal_properties')
        form_props = getattr(property_tool, 'form_properties')
        validators = form_props.getProperty(form, None)
#        self.log('getValidators: %s' % validators)
        if validators is None:
            return None
        validators = validators.strip()
        if validators == '':
            return []
        return validators.split(',')


    # expose ObjectManager's bad_id test to skin scripts
    def good_id(self, id):
        m = bad_id(id)
        if m is not None:
            return 0
        return 1


    def createForm(self):
        """Returns a CMFForm object"""
        # CMFForm wraps Formulator.BasicForm and provides some convenience methods that
        # make BasicForms easier to work with from external methods.
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
        # We intercept traversal when a form needs validation.  We insert a FormValidator object
        # into the traversal stack which, when published, does the proper validation and then
        # hands off to the navigation tool to determine the correct object to publish.

        # see if we are handling validation for this form
        validators = self.getValidators(name)
        if validators is None:
            # no -- do normal traversal
            target = getattr(aq_parent(self), name, None)
#            if name.endswith('.js'):
#                self.log('name: %s, target: <Javascript>, context: %s' % (name, str(aq_parent(self))), '__bobo_traverse__')
#            else:
#                self.log('name: %s, target: %s, context: %s' % (name, target, str(aq_parent(self))), '__bobo_traverse__')
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
        # We only need to invoke the validators for case (2)

        # see if we need to invoke validation
        errors = REQUEST.get(self.error_key, None)
        # Make sure errors is something generated by us, not something submitted via POST or GET
        if not type(errors) != type({}):
            errors = None
        form_submitted = REQUEST.get(FormTool.form_submitted_key, None)
#        self.log('errors = '+str(errors) + ', form_submitted = ' + str(form_submitted), '__bobo_traverse__')

        # We wrap the object in the acquisition layer of the parent of the FormTool
        # so that subsequent forms will operate on the FormTool's context and not
        # on the FormTool.
        do_validate = form_submitted and not errors
#        self.log('returning FormValidator(%s,%s,%s)' % (name, validators, do_validate), '__bobo_traverse__')
#        self.log(REQUEST.URL)
#        self.log(aq_parent(self))
        return FormValidator(name, validators, do_validate).__of__(aq_parent(self)) # wrap in acquisition layer


    # DEPRECATED
    def setValidator(self, form, validator):
        """Register a form validator"""
        return self.setValidators(form, [validator, 'validate_id'])

    # DEPRECATED
    security.declarePublic('getValidator')
    def getValidator(self, form):
        """Get the validator registered for a given form"""
        return self.getValidators(form)[0]

  
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
    # When a form needs validation, we publish a FormValidator object in place of the next form.
    # The FormValidator calls a validator method on the variables in the REQUEST and then
    # hands off to a page determined by the NavigationTool
    security = ClassSecurityInfo()

    def __init__(self, form, validators, do_validate):
        self.form = form
        self.validators = validators
        self.do_validate = do_validate


    security.declarePublic('__call__')
    def __call__(self, REQUEST, **kw):
        """ """
        trace = ['\n']
#        self.log('validator[%s] = \'%s\'' % (self.form, self.validators), '__call__')

        try:
            if self.do_validate:
                trace.append('Invoking validation')
                context = self.aq_parent
                # invoke validation
                (status, kwargs, trace) = self._validate(context, REQUEST, trace)
#                self.log('invoking validation, status = %s, kwargs = %s' % (status, kwargs))

                return context.portal_navigation.getNext(context, self.form, status, trace, **kwargs)
            else:
                trace.append('No validation needed.  Going to %s.%s' % (str(aq_parent(self)), self.form))
#                self.log('going to %s.%s' % (str(aq_parent(self)), self.form))
                target = getattr(aq_parent(self), self.form, None)
                return target(REQUEST, **kw)
        except NavigationError:
            raise
        except Exception, e:
            raise NavigationError(e, trace)


    index_html = None  # call __call__, not index_html


    def _validate(self, context, REQUEST, trace):
        """Execute validators on the validation stack then sets up the REQUEST and returns a status.
           Places a dictionary of errors in the REQUEST that is accessed via REQUEST[FormTool.error_key]
        """
        try:
            errors = {}
            status = 'success'  # default return value if the validator list is empty
            kwargs = {}
            for validator in self.validators:
                trace.append('Invoking %s' % validator)
#                self.log('calling validator [%s]' % (str(validator)))
                v = getattr(context, validator)
                (status, errors, kwargs) = mapply(v, REQUEST.args, REQUEST,
                                call_object, 1, missing_name, dont_publish_class,
                                REQUEST, bind=1)
                self.REQUEST.set('validation_status', status)
                self.REQUEST.set('errors', errors)
                for key in kwargs.keys():
                    self.REQUEST.set(key, kwargs[key])
                trace.append('\t -> (%s, %s, %s)' % (status, str(errors), str(kwargs)))
            trace.append('Validation returned (%s, %s)' % (status, str(kwargs)))
            return (status, kwargs, trace)
        except Exception, e:
            raise NavigationError(e, trace)


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
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
