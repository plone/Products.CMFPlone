# testcp.py
from zope import schema
from zope.interface import Interface
from plone.app.registry.browser.controlpanel import RegistryEditForm, ControlPanelFormWrapper
from plone.z3cform import layout

class IRecyleBinControlPanelSettings(Interface):
    recycling_enabled = schema.Bool(
        title=u"Enable the Recycle Bin",
        description=u"Enable or disable the Recycle Bin feature.",
        default=True,
    )

    retention_period = schema.Int(
        title=u"Retention Period",
        description=u"Number of days to keep deleted items in the Recycle Bin.",
        default=30,
    )

    maximum_size = schema.Int(
        title=u"Maximum Size",
        description=u"Maximum size of the Recycle Bin in MB.",
        default=100,
    )

class RecyclebinControlPanelForm(RegistryEditForm):
    schema = IRecyleBinControlPanelSettings
    schema_prefix = "plone-recyclebin"
    label = u"Recycler Settings"

RecyclebinControlPanelView = layout.wrap_form(RecyclebinControlPanelForm, ControlPanelFormWrapper)