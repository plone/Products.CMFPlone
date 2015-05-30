# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import INavigationSchema
from plone.app.registry.browser import controlpanel
from z3c.form.browser.checkbox import CheckBoxFieldWidget


class NavigationControlPanelForm(controlpanel.RegistryEditForm):

    id = "NavigationControlPanel"
    label = _(u"Navigation Settings")
    description = _(
        u"Lets you control how navigation is constructed in your site. " +
        u"Note that to control how the navigation tree is displayed, you " +
        u"should go to 'Manage portlets' at the root of the site (or " +
        u"wherever a navigation tree portlet has been added) and change " +
        u"its settings directly.")
    schema = INavigationSchema
    schema_prefix = "plone"

    def updateFields(self):
        super(NavigationControlPanelForm, self).updateFields()
        self.fields['displayed_types'].widgetFactory = \
            CheckBoxFieldWidget
        self.fields['workflow_states_to_show'].widgetFactory = \
            CheckBoxFieldWidget


class NavigationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = NavigationControlPanelForm
