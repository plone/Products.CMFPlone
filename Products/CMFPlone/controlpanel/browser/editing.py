from plone.app.registry.browser import controlpanel
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IEditingSchema
from z3c.form import interfaces


class EditingControlPanelForm(controlpanel.RegistryEditForm):
    id = "EditingControlPanel"
    label = _("Editing Settings")
    schema = IEditingSchema
    schema_prefix = "plone"

    def updateWidgets(self):
        super().updateWidgets()
        # hide the available_editors field/widgets
        self.widgets["available_editors"].mode = interfaces.HIDDEN_MODE


class EditingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = EditingControlPanelForm
