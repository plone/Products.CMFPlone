from logging import getLogger
from plone.app.registry.browser import controlpanel
from plone.base import PloneMessageFactory as _
from plone.base.interfaces.controlpanel import IImagingSchema


log = getLogger("Plone")


class ImagingControlPanelForm(controlpanel.RegistryEditForm):
    id = "ImagingSettings"
    label = _("Image Handling Settings")
    schema = IImagingSchema
    schema_prefix = "plone"


class ImagingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ImagingControlPanelForm
