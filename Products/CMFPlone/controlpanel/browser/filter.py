# -*- coding: utf-8 -*-
from plone.z3cform import layout
from Products.CMFPlone import PloneMessageFactory as _  # NOQA
from Products.CMFPlone.interfaces import IFilterSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.registry.browser import controlpanel
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button


class FilterControlPanel(controlpanel.RegistryEditForm):
    id = "FilterControlPanel"
    label = _(u"HTML Filtering Settings")
    description = _("Keep in mind that editors like TinyMCE might have "
                    "additional filters.")
    schema = IFilterSchema
    schema_prefix = "plone"
    form_name = _(u"HTML Filtering Settings")
    control_panel_view = "filter-controlpanel"

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):  # NOQA
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes saved."),
            "info")
        IStatusMessage(self.request).addStatusMessage(
            _(u"HTML generation is heavily cached across Plone. You may "
              u"have to edit existing content or restart your server to see "
              u"the changes."),
            "warning")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes canceled."),
            "info")
        self.request.response.redirect("%s/%s" % (
            self.context.absolute_url(),
            self.control_panel_view))


class ControlPanelFormWrapper(layout.FormWrapper):
    """Use this form as the plone.z3cform layout wrapper to get the control
    panel layout.
    """
    index = ViewPageTemplateFile('filter_controlpanel.pt')


FilterControlPanelView = layout.wrap_form(
    FilterControlPanel, ControlPanelFormWrapper)
