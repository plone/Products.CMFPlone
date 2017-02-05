# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IEditingSchema
from z3c.form import interfaces


class EditingControlPanelForm(controlpanel.RegistryEditForm):

    id = 'EditingControlPanel'
    label = _(u'Editing Settings')
    schema = IEditingSchema
    schema_prefix = 'plone'

    def updateWidgets(self):
        super(EditingControlPanelForm, self).updateWidgets()
        # hide the available_editors field/widgets
        self.widgets['available_editors'].mode = interfaces.HIDDEN_MODE


class EditingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = EditingControlPanelForm
