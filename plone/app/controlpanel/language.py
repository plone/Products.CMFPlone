from plone.app.form.widgets import LanguageDropdownChoiceWidget

from zope.formlib.form import FormFields
from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Choice

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.controlpanel.form import ControlPanelForm


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
        title=_(u"heading_site_language",
                default=u"Site language"),
        description=_(u"description_site_language",
                      default=u"The language used for the content and the UI "
                               "of this site."),
        required=True,
        vocabulary="plone.app.vocabularies.AvailableContentLanguages")


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
            context.supported_langs = [value]
        context.setDefaultLanguage(value)

    default_language = property(get_default_language,
                                set_default_language)

    def get_use_combined_language_codes(self):
        return aq_inner(self.context).use_combined_language_codes

    def set_use_combined_language_codes(self, value):
        context = aq_inner(self.context)
        # We are disabling the combined codes, but still have one selected
        # as the default.
        default = context.getDefaultLanguage()
        if len(default.split('-')) > 1:
            # XXX This should be done in some kind of validate method instead,
            # but I have no time to figure out that part of formlib right now
            request = context.REQUEST
            message = _(u"You cannot disable country-specific language "
                         "variants, please choose a different site "
                         "language first.")
            IStatusMessage(request).addStatusMessage(message, type='error')
        else:
            context.use_combined_language_codes = value

    use_combined_language_codes = property(get_use_combined_language_codes,
                                           set_use_combined_language_codes)


class LanguageControlPanel(ControlPanelForm):

    form_fields = FormFields(ILanguageSelectionSchema)
    form_fields['default_language'].custom_widget = LanguageDropdownChoiceWidget

    label = _(u"heading_language_settings", default="Language Settings")
    description = _(u"description_language_settings",
                    default="Settings related to interface languages and "
                            "content translations.")
    form_name = _(u"heading_language_settings", default="Language Settings")
