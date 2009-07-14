from zope import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary
from zope.formlib import form
from zope.app.form.browser import OrderedMultiSelectWidget

from plone.app.users.browser.userdata import IUserDataSchema
from plone.app.users.browser.joinform import JOIN_CONST


class IRegistrationSchema(Interface):

    join_form_fields = schema.Tuple(title=u'Join form fields',
                                    description=u'Select the fields for the join form')


def UserDataWidget(field, request):

    """ Create selector with schema fields vocab """

    values = [(f.__name__, f.__name__) for f in form.Fields(IUserDataSchema)]
    values = values + [(val, val) for val in JOIN_CONST]

    vocabulary = SimpleVocabulary.fromItems(values)

    return OrderedMultiSelectWidget(field, vocabulary, request)
