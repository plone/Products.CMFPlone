# -*- coding: utf-8 -*-
from logging import getLogger
from plone.app.registry.browser import controlpanel
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
from z3c.form import field
from z3c.form import group

log = getLogger('Plone')


def get_fields(fields_name):
    fields = field.Fields()
    for field_name in fields_name:
        fields += field.Fields(IImagingSchema.get(field_name))
    return fields


class DefaultImagingControlPanelForm(group.GroupForm):
    label = _(u"Default")
    fields = get_fields(['allowed_sizes', 'quality'])


class LeadImagingControlPanelForm(group.GroupForm):
    label = _(u"Leadimage")
    fields = get_fields(['lead_scale_name', 'is_lead_visible'])


class ImagingControlPanelForm(controlpanel.RegistryEditForm):

    id = "ImagingSettings"
    label = _(u"Image Handling Settings")
    schema = IImagingSchema
    schema_prefix = "plone"
    groups = (DefaultImagingControlPanelForm, LeadImagingControlPanelForm)


class ImagingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ImagingControlPanelForm
