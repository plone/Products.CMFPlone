from Interface import Base

class ICMFForm(Base):
    """ Wraps a Formulator BasicForm and provides convience methods to ease validation """
    
    def addField(field_id, fieldType, group=None, **kwargs):
        """ Adds a Formulator Field to a Form object
            The fieldType is referred to by the prefix 
            before Field in a Formulator field.  i.e.
            fieldType String == StringField 
        """

    def validate(self, REQUEST, errors=None):
        """ Iterates through the fields on the Form object and validates them.
            Errors can be passed in and will be appended to the errors dictionary.
            We will also strip the prefix of 'field_' in the REQUEST.form dictionary.
        """
        
class IFormTool(Base):
    """ FormTool handles Form validation, caching of Form validators and serves as a factory for portal_form objects.
    """
    
    def setValidators(form, validators=None):            
        """ Given a form id and a sequence of validators, update the validators.
        """

    def getValidators(form):
        """ Get the sequence of validators for a form id """

    def good_id(id):
        """ determines if the id is usable by an ObjectManager """

    def createForm():
        """ return a CMFForm object that provides some convience methods """

    def cacheValidator(key, validator):
        """ cache a validator by a key """

    def getCachedValidator(key):
        """ returns a cached validator or None """

    def setValidator(form, validator):
        """ sets a validator to a form id """

    def getValidator(form):
        """ returns the first validator for the form id """


