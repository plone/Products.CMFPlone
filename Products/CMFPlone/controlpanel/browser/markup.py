# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IMarkupSchema
from plone.app.registry.browser import controlpanel
from z3c.form.browser.checkbox import CheckBoxFieldWidget


class MarkupControlPanelForm(controlpanel.RegistryEditForm):

    id = "MarkupControlPanel"
    label = _(u"Markup Settings")
    schema = IMarkupSchema
    schema_prefix = "plone"

    def updateFields(self):
        super(MarkupControlPanelForm, self).updateFields()
        self.fields['allowed_types'].widgetFactory = \
            CheckBoxFieldWidget


class MarkupControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MarkupControlPanelForm
