# testcp.py
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from zope import schema
from zope.interface import Interface


class IRecycleBinControlPanelSettings(Interface):
    recycling_enabled = schema.Bool(
        title="Enable the recycle bin",
        description="Enable or disable the recycle bin feature.",
        default=False,
    )

    retention_period = schema.Int(
        title="Retention period",
        description="Number of days to keep deleted items in the recycle bin. Set to '0' to disable automatic purging.",
        default=30,
        min=0,
    )

    maximum_size = schema.Int(
        title="Maximum size",
        description="Maximum size of the recycle bin in MB. When the total size of items in the recycle bin exceeds its maximum size, the oldest items in the recycle bin will be permanently purged.",
        default=100,
        min=10,
    )


class RecyclebinControlPanelForm(RegistryEditForm):
    schema = IRecycleBinControlPanelSettings
    schema_prefix = "plone-recyclebin"
    label = "Recycle bin settings"
    description = "Settings for the Plone recycle bin"


RecyclebinControlPanelView = layout.wrap_form(
    RecyclebinControlPanelForm, ControlPanelFormWrapper
)
