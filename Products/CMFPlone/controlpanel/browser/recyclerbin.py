# testcp.py
from zope import schema
from zope.interface import Interface
from plone.app.registry.browser.controlpanel import RegistryEditForm, ControlPanelFormWrapper
from plone.z3cform import layout

class IRecycleBinControlPanelSettings(Interface):
    recycling_enabled = schema.Bool(
        title=u"Enable the Recycle Bin",
        description=u"Enable or disable the Recycle Bin feature.",
        default=True,
    )

    retention_period = schema.Int(
        title=u"Retention Period",
        description=u"Number of days to keep deleted items in the Recycle Bin.",
        default=30,
        min=1,
    )

    maximum_size = schema.Int(
        title=u"Maximum Size",
        description=u"Maximum size of the Recycle Bin in MB.",
        default=100,
        min=10,
    )
    
    auto_purge = schema.Bool(
        title=u"Auto Purge",
        description=u"Automatically purge items older than the retention period.",
        default=True,
    )

class RecyclebinControlPanelForm(RegistryEditForm):
    schema = IRecycleBinControlPanelSettings
    schema_prefix = "plone-recyclebin"
    label = u"Recycle Bin Settings"
    description = u"Settings for the Plone Recycle Bin functionality"

RecyclebinControlPanelView = layout.wrap_form(RecyclebinControlPanelForm, ControlPanelFormWrapper)