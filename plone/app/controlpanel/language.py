from plone.app.form.widgets import LanguageDropdownChoiceWidget

from zope.formlib.form import FormFields
from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import List

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import LanguageTableWidget


class ILanguageSelectionSchema(Interface):

    use_combined_language_codes = Bool(
        title=_(u'label_allow_combined_language_codes',
                default=u"Show country-specific language variants"),
        description=_(u"help_allow_combined_language_codes",
                      default=u"Examples: pt-br (Brazilian Portuguese), "
                               "en-us (American English) etc."),
        default=False,
        required=False)

    default_language = Choice(
        title=_(u"heading_default_language",
                default=u"Default language"),
        description=_(u"description_default_language",
                      default=u"If content requested is not available in the "
                               "language the user requested, content will be "
                               "presented in this default language."),
        required=True,
        vocabulary="plone.app.vocabularies.SupportedContentLanguages")

    supported_langs = List(
        title=_(u"heading_allowed_languages",
                default=u"Allowed languages"),
        description=_(u"description_allowed_languages",
                      default=u"Select the languages that can be added in "
                               "your portal."),
        required=True,
        missing_value=list('en'),
        value_type=Choice(
            vocabulary="plone.app.vocabularies.AvailableContentLanguages"))


class ILanguageSchema(ILanguageSelectionSchema):
    """Combined schema for the adapter lookup.
    """


class LanguageControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ILanguageSelectionSchema)

    def __init__(self, context):
        super(LanguageControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_languages')

    def get_default_language(self):
        return aq_inner(self.context).getDefaultLanguage()

    def set_default_language(self, value):
        context = aq_inner(self.context)
        if isinstance(value, tuple):
            value = value[0]
        supported_langs = context.getSupportedLanguages()
        if value not in supported_langs:
            value = supported_langs[0]
        context.setDefaultLanguage(value)

    default_language = property(get_default_language,
                                set_default_language)

    supported_langs = \
        ProxyFieldProperty(ILanguageSchema['supported_langs'])

    use_combined_language_codes = \
        ProxyFieldProperty(ILanguageSchema['use_combined_language_codes'])


class LanguageControlPanel(ControlPanelForm):

    form_fields = FormFields(ILanguageSelectionSchema)
    form_fields['default_language'].custom_widget = LanguageDropdownChoiceWidget
    form_fields['supported_langs'].custom_widget = LanguageTableWidget

    label = _(u"heading_language_settings", default="Language Settings")
    description = _(u"description_language_settings",
                    default="Settings related to interface languages and "
                            "content translations.")
    form_name = _(u"heading_language_settings", default="Language Settings")
