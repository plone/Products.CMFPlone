from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import getFieldNames
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.formlib import form
from zope.app.form.browser import OrderedMultiSelectWidget

from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.browser.register import JOIN_CONST

from zope.component import getUtility

_ = MessageFactory('plone')


class IRegistrationSchema(Interface):

    user_registration_fields = schema.Tuple(
        title=_(u'title_user_registration_fields', default=u'User registration fields'),

        description=_(u"description_user_registration_fields",
            default=(u"Select the fields for the join form. Fields in the "
            u"right box will be shown on the form, fields on the left are disabled. "
            u"Use the left/right buttons to move a field from right to left (to "
            u"disable it) and vice versa. Use the up/down buttons to change the order "
            u"in which the fields appear on the form."),
        )
    )


def UserDataWidget(field, request):
    """ Create selector with schema fields vocab """

    util = getUtility(IUserDataSchemaProvider)
    schema = util.getSchema()

    schemaFieldNames = getFieldNames(schema)

    values = [f.__name__ for f in form.Fields(schema)]
    values.extend([val for val in JOIN_CONST if val not in schemaFieldNames])
    terms = [SimpleTerm(v, v, v) for v in values]
    vocabulary = SimpleVocabulary(terms)

    return OrderedMultiSelectWidget(field, vocabulary, request)
