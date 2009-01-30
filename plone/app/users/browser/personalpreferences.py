#!/usr/bin/env python
# encoding: utf-8
"""
personalpreferences.py
"""

from zope.component import getUtility
from zope.interface import implements, Interface
from zope.component import adapts
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from zope.formlib import form
from zope.app.form.browser import SelectWidget

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from Products.PloneLanguageTool.interfaces import ILanguageTool

from plone.app.users.browser.form import AccountPanelForm

from plone.app.controlpanel.utils import SchemaAdapterBase
from plone.app.controlpanel import PloneMessageFactory as _



class IPersonalPreferences(Interface):

    """ Provide schema for pesonalize form """


    start_page = schema.TextLine(title=u'Start page',
                               description=u'Start page.')

    #wysiwyg_editor = schema.TextLine(title=u'Wysiwyg editor',
    #                                 description=u'Wysiwyg editor to use.')

    language = schema.TextLine(title=u'Language',
                                     description=u'Your preferred language.')


class PersonalPreferencesPanelAdapter(SchemaAdapterBase):

    adapts(ISiteRoot)
    implements(IPersonalPreferences)

    def __init__(self, context):

        mt = getToolByName(context, 'portal_membership')
        
        if mt.isAnonymousUser():
            raise "Can't modify properties of anonymous user"
        else:
            self.context = mt.getAuthenticatedMember()


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
    
    language_tool = getUtility(ISiteRoot).portal_languages

    languages = language_tool.listSupportedLanguages()
    
    vocabulary = SimpleVocabulary.fromItems(languages)
    
    return SelectWidget(field, vocabulary, request)


def WysiwygEditorWidget(field, request):

    """ Create selector with available editors """
    
    site_props = getUtility(ISiteRoot).portal_properties.site_properties

    editors = site_props.available_editors
    
    vocabulary = SimpleVocabulary.fromItems((ed, ed) for ed in editors)
    
    return SelectWidget(field, vocabulary, request)


class PersonalPreferencesPanel(AccountPanelForm):
    """ Implementation of personalize form that uses formlib """

    form_fields = form.FormFields(IPersonalPreferences)
    
    label = _(u"Personal preferences")
    description = _(u"Set your prefs here dude!.")

    form_fields['language'].custom_widget = LanguageWidget
    #form_fields['wysiwyg_editor'].custom_widget = WysiwygEditorWidget

    form_name = _(u'Personal Preferences Form')
