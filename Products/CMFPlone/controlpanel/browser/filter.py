# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _  # NOQA
from Products.CMFPlone.interfaces import IFilterSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform import layout
from z3c.form import form


class FilterControlPanel(AutoExtensibleForm, form.EditForm):
    id = "FilterControlPanel"
    label = _(u"Filter settings")
    description = _("Filter settings.")
    schema = IFilterSchema
    form_name = _(u"Filter Settings")
    control_panel_view = "filter-controlpanel"


class ControlPanelFormWrapper(layout.FormWrapper):
    """Use this form as the plone.z3cform layout wrapper to get the control
    panel layout.
    """
    index = ViewPageTemplateFile('filter_controlpanel.pt')


FilterControlPanelView = layout.wrap_form(
    FilterControlPanel, ControlPanelFormWrapper)
