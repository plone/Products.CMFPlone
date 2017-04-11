from plone.app.registry.browser import controlpanel
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
from Products.CMFPlone.interfaces.controlpanel import ILeadImagingSchema
from Products.CMFPlone.interfaces.controlpanel import IDefaultImagingSchema
from z3c.form import field
from z3c.form import group

from logging import getLogger
log = getLogger('Plone')


class DefaultImagingControlPanelForm(group.GroupForm):
    label = _(u"Default")
    fields = field.Fields(IDefaultImagingSchema)


class LeadImagingControlPanelForm(group.GroupForm):
    label = _(u"Leadimage")
    fields = field.Fields(ILeadImagingSchema)

class ImagingControlPanelForm(controlpanel.RegistryEditForm):

    id = "ImagingSettings"
    label = _(u"Image Handling Settings")
    schema = IImagingSchema
    schema_prefix = "plone"
    groups = (DefaultImagingControlPanelForm, LeadImagingControlPanelForm)


class ImagingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = ImagingControlPanelForm
