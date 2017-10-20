# -*- coding: utf-8 -*-
from logging import getLogger
from plone.app.registry.browser import controlpanel
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema

log = getLogger('Plone')


class ImagingControlPanelForm(controlpanel.RegistryEditForm):

    id = "ImagingSettings"
    label = _(u"Image Handling Settings")
    schema = IImagingSchema
    schema_prefix = "plone"


class ImagingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ImagingControlPanelForm
