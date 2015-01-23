# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IFilterSchema
from plone.app.registry.browser import controlpanel
from plone.formwidget.namedfile.widget import NamedImageFieldWidget


class FilterControlPanelForm(controlpanel.RegistryEditForm):

    id = "FilterControlPanel"
    label = _(u"Filter settings")
    description = _("Filter settings.")
    schema = IFilterSchema
    schema_prefix = "plone"


class FilterControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FilterControlPanelForm
