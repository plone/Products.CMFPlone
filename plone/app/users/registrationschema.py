from zope import schema
from zope.schema import getFieldNames
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary
from zope.formlib import form
from zope.app.form.browser import OrderedMultiSelectWidget

from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.browser.joinform import JOIN_CONST

from zope.component import getUtility


class IRegistrationSchema(Interface):

    join_form_fields = schema.Tuple(
        title=u'Join form fields',

        description=u"""Select the fields for the join form. Fields in the
        right' box will be shown on the form, fields on the left are disabled.
        Use the left/right buttons to move a field from right to left (to
        disable it) and vice versa. Use the up/down buttons to change the order
        in which the fields appear on the form.""",

        )


def UserDataWidget(field, request):

    """ Create selector with schema fields vocab """

    util = getUtility(IUserDataSchemaProvider)
    schema = util.getSchema()
    
    schemaFieldNames = getFieldNames(schema)
    
    values = [(f.__name__, f.__name__) for f in form.Fields(schema)]
    values = values + [(val, val) for val in JOIN_CONST if val not in schemaFieldNames]

    vocabulary = SimpleVocabulary.fromItems(values)

    return OrderedMultiSelectWidget(field, vocabulary, request)
