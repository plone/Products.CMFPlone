from zope.component import getUtility
from zope.interface import implements, Interface
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.formlib import form
from zope.app.form.browser import DropdownWidget
from zope.app.form.browser import SelectWidget

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _
from plone.app.users.browser.schema_adapter import AccountPanelSchemaAdapter
from plone.app.users.browser.form import AccountPanelForm


class IPersonalPreferences(Interface):

    """ Provide schema for pesonalize form """


    start_page = schema.TextLine(title=u'Start page',
                                 description=u'Start page.',
                                 required=False)

    #wysiwyg_editor = schema.Choice(title=u'Wysiwyg editor',
    #                            vocabulary=""
    #                            description=u'Wysiwyg editor to use.')

    language = schema.Choice(title=_(u'label_language', default=u'Language'),
                               description=_(u'help_preferred_language', u'Your preferred language.'),
                               vocabulary="plone.app.vocabularies.AvailableContentLanguages",
                               required=False)


class PersonalPreferencesPanelAdapter(AccountPanelSchemaAdapter):

    implements(IPersonalPreferences)


    def get_start_page(self):
        return self.context.getProperty('start_page', '')

    def set_start_page(self, value):
        return self.context.setMemberProperties({'start_page': value})

    start_page = property(get_start_page, set_start_page)


    def get_wysiwyg_editor(self):
        return self.context.getProperty('wysiwyg_editor', '')

    def set_wysiwyg_editor(self, value):
        return self.context.setProperty('wysiwyg_editor', value)

    wysiwyg_editor = property(get_wysiwyg_editor, set_wysiwyg_editor)


    def get_language(self):
        return self.context.getProperty('language', '')

    def set_language(self, value):
        return self.context.setMemberProperties({'language': value})

    language = property(get_language, set_language)


def LanguageWidget(field, request):

    """ Create selector with languages vocab """
    
    widget = DropdownWidget(field, field.vocabulary, request)
    widget._messageNoValue = _(u"vocabulary-missing-single-value-for-edit",
                        u"Language neutral (site default)")
    return widget


def WysiwygEditorWidget(field, request):

    """ Create selector with available editors """

    portal = getUtility(ISiteRoot)
    site_props = getToolByName(portal, 'portal_properties').site_properties

    editors = site_props.available_editors
    
    vocabulary = SimpleVocabulary.fromItems((ed, ed) for ed in editors)
    
    return SelectWidget(field, vocabulary, request)


class PersonalPreferencesPanel(AccountPanelForm):
    """ Implementation of personalize form that uses formlib """

    label = _(u"heading_my_preferences", default=u"Personal preferences")
    description = _(u"description_my_preferences", default=u"Your personal settings.")
    form_name = _(u'legend_personal_details', u'Personal Details')

    form_fields = form.FormFields(IPersonalPreferences)
    form_fields['language'].custom_widget = LanguageWidget
    #form_fields['wysiwyg_editor'].custom_widget = WysiwygEditorWidget

