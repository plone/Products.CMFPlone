from plone.app.registry.browser import controlpanel
from plone.base.interfaces import IMarkupSchema
from Products.CMFPlone import PloneMessageFactory as _
from z3c.form.browser.checkbox import CheckBoxFieldWidget


class MarkupControlPanelForm(controlpanel.RegistryEditForm):

    id = "MarkupControlPanel"
    label = _("Markup Settings")
    schema = IMarkupSchema
    schema_prefix = "plone"

    def updateFields(self):
        super().updateFields()
        self.fields['allowed_types'].widgetFactory = \
            CheckBoxFieldWidget


class MarkupControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MarkupControlPanelForm
