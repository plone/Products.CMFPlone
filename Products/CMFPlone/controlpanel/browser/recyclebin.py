from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.base.interfaces.recyclebin import IRecycleBinControlPanelSettings
from plone.z3cform import layout


class RecyclebinControlPanelForm(RegistryEditForm):
    schema = IRecycleBinControlPanelSettings
    schema_prefix = "plone-recyclebin"
    label = "Recycle bin settings"
    description = "Settings for the Plone recycle bin"


RecyclebinControlPanelView = layout.wrap_form(
    RecyclebinControlPanelForm, ControlPanelFormWrapper
)
