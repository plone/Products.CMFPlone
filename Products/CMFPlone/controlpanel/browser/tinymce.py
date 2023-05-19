from plone.app.registry.browser import controlpanel
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import ITinyMCEAdvancedSchema
from plone.base.interfaces import ITinyMCELayoutSchema
from plone.base.interfaces import ITinyMCEPluginSchema
from plone.base.interfaces import ITinyMCEResourceTypesSchema
from plone.base.interfaces import ITinyMCESchema
from plone.base.interfaces import ITinyMCESpellCheckerSchema
from z3c.form import field
from z3c.form import group
from z3c.form.browser.checkbox import CheckBoxFieldWidget


class TinyMCEPluginForm(group.GroupForm):
    label = _("Plugins and Toolbar")
    fields = field.Fields(ITinyMCEPluginSchema)


class TinyMCESpellCheckerForm(group.GroupForm):
    label = _("Spell Checker")
    fields = field.Fields(ITinyMCESpellCheckerSchema)


class TinyMCEResourceTypesForm(group.GroupForm):
    label = _("Resource Types")
    fields = field.Fields(ITinyMCEResourceTypesSchema)


class TinyMCEAdvancedForm(group.GroupForm):
    label = _("Advanced")
    fields = field.Fields(ITinyMCEAdvancedSchema)


class TinyMCEControlPanelForm(controlpanel.RegistryEditForm):
    id = "TinyMCEControlPanel"
    label = _("TinyMCE Settings")
    schema = ITinyMCESchema
    schema_prefix = "plone"
    fields = field.Fields(ITinyMCELayoutSchema)
    groups = (
        TinyMCEPluginForm,
        TinyMCESpellCheckerForm,
        TinyMCEResourceTypesForm,
        TinyMCEAdvancedForm,
    )

    def updateFields(self):
        super().updateFields()
        self.groups[0].fields["plugins"].widgetFactory = CheckBoxFieldWidget


class TinyMCEControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TinyMCEControlPanelForm
