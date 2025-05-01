# testcp.py
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class IRecycleBinControlPanelSettings(Interface):
    recycling_enabled = schema.Bool(
        title="Enable the Recycle Bin",
        description="Enable or disable the Recycle Bin feature.",
        default=True,
    )

    retention_period = schema.Int(
        title="Retention Period",
        description="Number of days to keep deleted items in the Recycle Bin. Set to 0 to disable automatic purging.",
        default=30,
        min=0,
    )

    maximum_size = schema.Int(
        title="Maximum Size",
        description="Maximum size of the Recycle Bin in MB.",
        default=100,
        min=10,
    )


class RecyclebinControlPanelForm(RegistryEditForm):
    schema = IRecycleBinControlPanelSettings
    schema_prefix = "plone-recyclebin"
    label = "Recycle Bin Settings"
    description = "Settings for the Plone Recycle Bin functionality"


RecyclebinControlPanelView = layout.wrap_form(
    RecyclebinControlPanelForm, ControlPanelFormWrapper
)
