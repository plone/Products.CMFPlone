from plone.fieldsets import FormFieldsets
from plone.app.form.widgets import DisabledCheckBoxWidget
from plone.app.form.widgets import LanguageDropdownChoiceWidget

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

    display_flags = Bool(
        title=_(u'label_display_flags',
                default=u"Display flags for language selection"),
                description=_(u"help_display_flags",
                              default=u"(May be politically sensitive in some "
                                       "areas, do not use this unless you "
                                       "know that it is acceptable)."),
                default=False,
                required=False)

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


class ILanguageNegotiationSchema(Interface):

    use_path_negotiation = Bool(
        title=_(u'label_language_codes_in_url',
                default=u"Use language codes in URL path for manual override."),
        default=True,
        required=False)

    use_cookie_negotiation = Bool(
        title=_(u'label_cookies_for_override',
                default=u"Use cookie for manual override."),
        default=True,
        required=False)

    use_cctld_negotiation = Bool(
        title=_(u'label_ccTLD_language',
                default=u"Use the virtual hostname of the Plone site."),
        default=False,
        required=False)

    use_request_negotiation = Bool(
        title=_(u'label_browser_language_negotiation',
                default=u"Use browser language request negotiation."),
        default=True,
        required=False)

    use_default_language = Bool(
        title=_(u'text_default_fallback',
                default=u"Default fallback (always enabled). This is the "
                         "language specified as default above."),
        default=True,
        required=False)


class IMultilingualContentSchema(Interface):

    force_language_urls = Bool(
        title=_(u'label_force_different_urls',
                default=u"Force different URLs for each language (redirect)."),
        default=True,
        required=False)

    start_neutral = Bool(
        title=_(u'label_start_neutral',
                default=u"Create content initially as neutral language."),
        default=True,
        required=False)


class ILanguageSchema(ILanguageSelectionSchema,
                      ILanguageNegotiationSchema,
                      IMultilingualContentSchema):
    """Combined schema for the adapter lookup.
    """


class LanguageControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ILanguageSchema)

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

    display_flags = \
        ProxyFieldProperty(ILanguageSchema['display_flags'])

    use_combined_language_codes = \
        ProxyFieldProperty(ILanguageSchema['use_combined_language_codes'])

    use_path_negotiation = \
        ProxyFieldProperty(ILanguageSchema['use_path_negotiation'])

    use_cookie_negotiation = \
        ProxyFieldProperty(ILanguageSchema['use_cookie_negotiation'])

    use_request_negotiation = \
        ProxyFieldProperty(ILanguageSchema['use_request_negotiation'])

    use_cctld_negotiation = \
        ProxyFieldProperty(ILanguageSchema['use_cctld_negotiation'])

    use_default_language = True

    force_language_urls = \
        ProxyFieldProperty(ILanguageSchema['force_language_urls'])

    start_neutral = \
        ProxyFieldProperty(ILanguageSchema['start_neutral'])


languageselectionset = FormFieldsets(ILanguageSelectionSchema)
languageselectionset.id = 'languageselection'
languageselectionset.label = _(u'label_language_selection',
                               default=u'Selection')

languagenegotiationset = FormFieldsets(ILanguageNegotiationSchema)
languagenegotiationset.id = 'languagenegotiation'
languagenegotiationset.label = _(u'label_language_negotiation',
                                 default=u'Negotiation')
languagenegotiationset.description = _(u'description_negotiation_scheme',
                                       default=u"Check the language "
                                                "negotiation schemes that "
                                                "apply to this site.")

multilingualcontentset = FormFieldsets(IMultilingualContentSchema)
multilingualcontentset.id = 'multilingualcontent'
multilingualcontentset.label = _(u'label_multilingual_content',
                                 default=u'Multilingual Content')
multilingualcontentset.description = _(u'description_content_settings',
                                       default=u"Check the settings that "
                                                "apply to multilingual "
                                                "content.")


class LanguageControlPanel(ControlPanelForm):

    form_fields = FormFieldsets(languageselectionset,
                                languagenegotiationset,
                                multilingualcontentset)
    form_fields['default_language'].custom_widget = LanguageDropdownChoiceWidget
    form_fields['supported_langs'].custom_widget = LanguageTableWidget
    form_fields['use_default_language'].custom_widget = DisabledCheckBoxWidget
    label = _(u"heading_language_settings", default="Language Settings")
    description = _(u"description_language_settings",
                    default="Settings related to interface languages and "
                            "content translations.")
    form_name = _(u"heading_language_settings", default="Language Settings")
