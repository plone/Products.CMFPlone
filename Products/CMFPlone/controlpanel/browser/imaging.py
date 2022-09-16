from logging import getLogger
from plone.app.registry.browser import controlpanel
from plone.base.interfaces.controlpanel import IImagingSchema
from Products.CMFPlone import PloneMessageFactory as _


log = getLogger('Plone')


class ImagingControlPanelForm(controlpanel.RegistryEditForm):

    id = "ImagingSettings"
    label = _("Image Handling Settings")
    schema = IImagingSchema
    schema_prefix = "plone"


class ImagingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ImagingControlPanelForm
