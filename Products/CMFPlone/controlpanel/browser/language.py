# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.registry.browser import controlpanel

from Products.CMFPlone.interfaces import ILanguageSchema
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button


class LanguageControlPanelForm(controlpanel.RegistryEditForm):

    id = "LanguageControlPanel"
    label = _(u"heading_language_settings", default="Language Settings")
    description = _(u"description_language_settings",
                    default="Settings related to interface languages and "
                            "content translations.")

    schema = ILanguageSchema
    schema_prefix = "plone"

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        # We need to check if the default language is in available languages
        if 'default_language' in data and 'available_languages' in data and \
                data['default_language'] not in data['available_languages']:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Default language not in available languages"),
                "error")

            # e = Invalid(_(u"Default language not in available languages"))
            # raise WidgetActionExecutionError('default_language', e)
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes saved."),
            "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes canceled."),
            "info")
        self.request.response.redirect("%s/%s" % (
            self.context.absolute_url(),
            self.control_panel_view))


class LanguageControlPanel(controlpanel.ControlPanelFormWrapper):
    form = LanguageControlPanelForm


#class LanguageControlPanel(ControlPanelForm):
#    form_fields = FormFields(ILanguageSchema)
#    form_fields['default_language'].custom_widget = \
#       LanguageDropdownChoiceWidget
#
#    form_name = _(u"heading_language_settings", default="Language Settings")
