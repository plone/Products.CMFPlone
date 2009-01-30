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

#from Acquisition import aq_inner, aq_base
#from Products.CMFPlone import utils
from Products.Five.browser import BrowserView

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from Products.PloneLanguageTool.interfaces import ILanguageTool

from plone.app.users.browser.form import AccountPanelForm

from plone.app.controlpanel.utils import SchemaAdapterBase
from plone.app.controlpanel import PloneMessageFactory as _



class IPersonalPreferences(Interface):

    """ Provide schema for pesonalize form """

    fullname = schema.TextLine(title=u'Fullname',
                               description=u'Full name')

    email = schema.TextLine(title=u'Email',
                               description=u'Email')
    
    home_page = schema.TextLine(title=u'Home page',
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


    def get_email(self):
        return self.context.getProperty('email', '')

    def set_email(self, value):
        return self.context.setMemberProperties({'email': value})

    email = property(get_email, set_email)


    def get_fullname(self):
        return self.context.getProperty('fullname', '')

    def set_fullname(self, value):
        return self.context.setMemberProperties({'fullname': value})

    fullname = property(get_fullname, set_fullname)


    def get_home_page(self):
        return self.context.getProperty('home_page', '')

    def set_home_page(self, value):
        return self.context.setMemberProperties({'home_page': value})

    home_page = property(get_home_page, set_home_page)


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
