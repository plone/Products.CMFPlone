from plone.app.registry.browser import controlpanel
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IFilterSchema
from plone.z3cform import layout
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button


class FilterControlPanel(controlpanel.RegistryEditForm):
    id = "FilterControlPanel"
    label = _("HTML Filtering Settings")
    description = _(
        "Keep in mind that editors like TinyMCE might have " "additional filters."
    )
    schema = IFilterSchema
    schema_prefix = "plone"
    form_name = _("HTML Filtering Settings")
    control_panel_view = "filter-controlpanel"

    @button.buttonAndHandler(_("Save"), name="save")
    def handleSave(self, action):  # NOQA
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(_("Changes saved."), "info")
        IStatusMessage(self.request).addStatusMessage(
            _(
                "HTML generation is heavily cached across Plone. You may "
                "have to edit existing content or restart your server to see "
                "the changes."
            ),
            "warning",
        )
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_("Cancel"), name="cancel")
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(_("Changes canceled."), "info")
        self.request.response.redirect(
            f"{self.context.absolute_url()}/{self.control_panel_view}"
        )


class ControlPanelFormWrapper(layout.FormWrapper):
    """Use this form as the plone.z3cform layout wrapper to get the control
    panel layout.
    """

    index = ViewPageTemplateFile("filter_controlpanel.pt")


FilterControlPanelView = layout.wrap_form(FilterControlPanel, ControlPanelFormWrapper)
