# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _  # NOQA
from Products.CMFPlone.interfaces import IFilterSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.autoform.form import AutoExtensibleForm
from plone.z3cform import layout
from z3c.form import button
from z3c.form import form
from Products.PortalTransforms.transforms.safe_html import VALID_TAGS
from Products.PortalTransforms.transforms.safe_html import NASTY_TAGS


class FilterControlPanel(AutoExtensibleForm, form.EditForm):
    id = "FilterControlPanel"
    label = _(u"HTML Filtering Settings")
    description = ""
    schema = IFilterSchema
    form_name = _(u"HTML Filtering Settings")
    control_panel_view = "filter-controlpanel"

    def updateActions(self):  # NOQA
        """Have to override this because we only have Save, not Cancel
        """
        super(FilterControlPanel, self).updateActions()
        self.actions['save'].addClass("context")

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):  # NOQA
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Save in portal tools
        safe_html = getattr(
            getToolByName(self.context, 'portal_transforms'),
            'safe_html',
            None)

        nasty_tags = data['nasty_tags']
        custom_tags = data['custom_tags']
        stripped_tags = data['stripped_tags']

        valid = safe_html._config['valid_tags']

        # start with removing tags that do not belong in valid tags
        for value in nasty_tags + stripped_tags:
            if value in valid:
                del valid[value]
        # add in custom tags
        for custom in custom_tags:
            if value not in valid:
                valid[custom] = 1
        # then, check if something was previously prevented but is no longer
        for tag in set(VALID_TAGS.keys()) - set(valid.keys()):
            if tag not in nasty_tags and tag not in stripped_tags:
                valid[tag] = VALID_TAGS[tag]

        # nasty tags are simple, just set the value here
        nasty_value = {}
        for tag in nasty_tags:
            nasty_value[tag] = NASTY_TAGS.get(tag, VALID_TAGS.get(tag, 1))
        safe_html._config['nasty_tags'] = nasty_value

        disable_filtering = int(data['disable_filtering'])
        if disable_filtering != safe_html._config['disable_transform']:
            safe_html._config['disable_transform'] = disable_filtering

        for attr in ('stripped_combinations', 'class_blacklist',
                     'stripped_attributes', 'style_whitelist'):
            value = data[attr]
            if value is None:
                if attr == 'stripped_combinations':
                    value = {}
                else:
                    value = []
            if value != safe_html._config[attr]:
                safe_html._config[attr] = value

        # always reload the transform
        safe_html._p_changed = True
        safe_html.reload()

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


class ControlPanelFormWrapper(layout.FormWrapper):
    """Use this form as the plone.z3cform layout wrapper to get the control
    panel layout.
    """
    index = ViewPageTemplateFile('filter_controlpanel.pt')


FilterControlPanelView = layout.wrap_form(
    FilterControlPanel, ControlPanelFormWrapper)
