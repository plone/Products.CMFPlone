from plone.app.registry.browser import controlpanel
from plone.base import PloneMessageFactory as _
from plone.i18n.interfaces import ILanguageSchema
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button


class LanguageControlPanelForm(controlpanel.RegistryEditForm):
    id = "LanguageControlPanel"
    label = _("heading_language_settings", default="Language Settings")
    description = _(
        "description_language_settings",
        default="Settings related to interface languages and " "content translations.",
    )

    schema = ILanguageSchema
    schema_prefix = "plone"

    @button.buttonAndHandler(_("Save"), name="save")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        # We need to check if the default language is in available languages
        if (
            "default_language" in data
            and "available_languages" in data
            and data["default_language"] not in data["available_languages"]
        ):
            IStatusMessage(self.request).addStatusMessage(
                _("Default language not in available languages"), "error"
            )

            # e = Invalid(_(u"Default language not in available languages"))
            # raise WidgetActionExecutionError('default_language', e)
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_("Changes saved."), "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name="cancel")
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(
            f"{self.context.absolute_url()}/{self.control_panel_view}"
        )


class LanguageControlPanel(controlpanel.ControlPanelFormWrapper):
    form = LanguageControlPanelForm
