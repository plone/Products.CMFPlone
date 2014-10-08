from z3c.form.browser.checkbox import CheckBoxFieldWidget
from plone.app.registry.browser import controlpanel

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IMarkupSchema


class MarkupControlPanelForm(controlpanel.RegistryEditForm):

    id = "MarkupControlPanel"
    label = _(u"Markup settings")
    schema = IMarkupSchema
    schema_prefix = "plone"

    def updateFields(self):
        super(MarkupControlPanelForm, self).updateFields()
        self.fields['allowed_types'].widgetFactory = \
            CheckBoxFieldWidget


class MarkupControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MarkupControlPanelForm
