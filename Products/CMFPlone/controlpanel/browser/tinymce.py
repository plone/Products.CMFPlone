from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ITinyMCELayoutSchema
from Products.CMFPlone.interfaces import ITinyMCESpellCheckerSchema
from Products.CMFPlone.interfaces import ITinyMCEResourceTypesSchema
from Products.CMFPlone.interfaces import ITinyMCESchema
from Products.CMFPlone.interfaces import ITinyMCEPluginSchema
from plone.app.registry.browser import controlpanel
from z3c.form import field
from z3c.form import group
from z3c.form.browser.checkbox import CheckBoxFieldWidget


class TinyMCEPluginForm(group.GroupForm):
    label = _(u"Plugins and Toolbar")
    fields = field.Fields(ITinyMCEPluginSchema)


class TinyMCESpellCheckerForm(group.GroupForm):
    label = _(u"Spell Checker")
    fields = field.Fields(ITinyMCESpellCheckerSchema)


class TinyMCEResourceTypesForm(group.GroupForm):
    label = _(u"Resource Types")
    fields = field.Fields(ITinyMCEResourceTypesSchema)


class TinyMCEControlPanelForm(controlpanel.RegistryEditForm):

    id = "TinyMCEControlPanel"
    label = _(u"TinyMCE Settings")
    schema = ITinyMCESchema
    schema_prefix = "plone"
    fields = field.Fields(ITinyMCELayoutSchema)
    groups = (TinyMCEPluginForm, TinyMCESpellCheckerForm,
              TinyMCEResourceTypesForm)

    def updateFields(self):
        super(TinyMCEControlPanelForm, self).updateFields()
        self.groups[0].fields['plugins'].widgetFactory = CheckBoxFieldWidget


class TinyMCEControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TinyMCEControlPanelForm
