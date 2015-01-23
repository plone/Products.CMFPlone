# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _  # NOQA
from Products.CMFPlone.interfaces import IFilterSchema
from plone.app.registry.browser import controlpanel


class FilterControlPanelForm(controlpanel.RegistryEditForm):

    id = "FilterControlPanel"
    label = _(u"Filter settings")
    description = _("Filter settings.")
    schema = IFilterSchema
    schema_prefix = "plone"


class FilterControlPanel(controlpanel.ControlPanelFormWrapper):
    form = FilterControlPanelForm
