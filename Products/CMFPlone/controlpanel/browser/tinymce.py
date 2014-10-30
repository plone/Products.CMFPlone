from plone.app.registry.browser import controlpanel

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ITinyMCESchema
from Products.CMFPlone.interfaces import ITinyMCEPatternSchema
from Products.CMFPlone.interfaces import ITinyMCELayoutSchema
from Products.CMFPlone.interfaces import ITinyMCEToolbarSchema
from Products.CMFPlone.interfaces import ITinyMCELibrariesSchema
from Products.CMFPlone.interfaces import ITinyMCEResourceTypesSchema
from z3c.form import group
from z3c.form import field


class TinyMCEPatternForm(group.GroupForm):
    label = _(u"Pattern")
    fields = field.Fields(ITinyMCEPatternSchema)


class TinyMCEToolbarForm(group.GroupForm):
    label = _(u"Toolbar")
    fields = field.Fields(ITinyMCEToolbarSchema)


class TinyMCELibrariesForm(group.GroupForm):
    label = _(u"Libraries")
    fields = field.Fields(ITinyMCELibrariesSchema)


class TinyMCEResourceTypesForm(group.GroupForm):
    label = _(u"Resource Types")
    fields = field.Fields(ITinyMCEResourceTypesSchema)


class TinyMCEControlPanelForm(controlpanel.RegistryEditForm):

    id = "TinyMCEControlPanel"
    label = _(u"TinyMCE settings")
    schema = ITinyMCESchema
    schema_prefix = "plone"
    fields = field.Fields(ITinyMCELayoutSchema)
    groups = (TinyMCEToolbarForm, TinyMCELibrariesForm,
              TinyMCEResourceTypesForm, TinyMCEPatternForm)


class TinyMCEControlPanel(controlpanel.ControlPanelFormWrapper):
    form = TinyMCEControlPanelForm
