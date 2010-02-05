from Acquisition import aq_inner

from zope.interface import implements, Interface
from zope.schema import Choice
from zope.schema import Bool
from zope.formlib import form
from zope.app.form.browser import DropdownWidget

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.users.browser.schema_adapter import AccountPanelSchemaAdapter
from plone.app.users.browser.account import AccountPanelForm


class IPersonalPreferences(Interface):

    """ Provide schema for pesonalize form """

    wysiwyg_editor = Choice(title=u'Wysiwyg editor',
                            description=u'Wysiwyg editor to use.',
                            vocabulary="plone.app.vocabularies.AvailableEditors",
                            required=False)
    ext_editor = Bool(title=_(u'label_ext_editor', default=u'Enable external editing'),
                           description=u'When checked, an option will be '
                               'made visible on each page which allows you '
                               'to edit content with your favorite editor '
                               'instead of using browser-based editors. This '
                               'requires an additional application, most often '
                               'ExternalEditor or ZopeEditManager, installed '
                               'client-side. Ask your administrator for more '
                               'information if needed.')
    listed = Bool(title=_(u'label_listed_status', default=u'Listed in searches'),
                           description=u'Determines if your user name is listed in user '
                                        'searches done on this site.',
                           required=False)
    visible_ids = Bool(title=_(u'label_edit_short_names', default=u'Allow editing of Short Names'),
                           description=u'Determines if Short Names (also known '
                               'as IDs) are changable when editing items. If Short '
                               'Names are not displayed, they will be generated automatically.',
                           required=False)
    language = Choice(title=_(u'label_language', default=u'Language'),
                           description=_(u'help_preferred_language', u'Your preferred language.'),
                           vocabulary="plone.app.vocabularies.AvailableContentLanguages",
                           required=False)


class PersonalPreferencesPanelAdapter(AccountPanelSchemaAdapter):

    implements(IPersonalPreferences)

    def get_wysiwyg_editor(self):
        return self.context.getProperty('wysiwyg_editor', '')

    def set_wysiwyg_editor(self, value):
        return self.context.setMemberProperties({'wysiwyg_editor': value})

    wysiwyg_editor = property(get_wysiwyg_editor, set_wysiwyg_editor)


    def get_ext_editor(self):
        return self.context.getProperty('ext_editor', '')

    def set_ext_editor(self, value):
        return self.context.setMemberProperties({'ext_editor': value})

    ext_editor = property(get_ext_editor, set_ext_editor)
 
 
    def get_listed(self):
        return self.context.getProperty('listed', '')

    def set_listed(self, value):
        return self.context.setMemberProperties({'listed': value})

    listed = property(get_listed, set_listed)
    
    
    def get_visible_ids(self):
        return self.context.getProperty('visible_ids', '')

    def set_visible_ids(self, value):
        return self.context.setMemberProperties({'visible_ids': value})

    visible_ids = property(get_visible_ids, set_visible_ids)


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

    widget = DropdownWidget(field, field.vocabulary, request)
    widget._messageNoValue = _(u"vocabulary-available-editor-novalue",
                        u"None")
    return widget




class PersonalPreferencesPanel(AccountPanelForm):
    """ Implementation of personalize form that uses formlib """

    label = _(u"heading_my_preferences", default=u"Personal Preferences")
    description = _(u"description_my_preferences", default=u"Your personal settings.")
    form_name = _(u'legend_personal_details', u'Personal Details')

    form_fields = form.FormFields(IPersonalPreferences)
    form_fields['language'].custom_widget = LanguageWidget
    form_fields['wysiwyg_editor'].custom_widget = WysiwygEditorWidget 
    

    def setUpWidgets(self, ignore_request=False):
        """ Hide the visible_ids field based on portal_properties.
        """
        context = aq_inner(self.context)
        properties = getToolByName(context, 'portal_properties')
        siteProperties = properties.site_properties
        
        if not siteProperties.visible_ids:
            self.hidden_widgets.append('visible_ids')
        
        super(PersonalPreferencesPanel, self).setUpWidgets(ignore_request)  
        
        

          
