from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import INavigationSchema
from plone.app.registry.browser import controlpanel
from z3c.form.browser.checkbox import CheckBoxFieldWidget


class NavigationControlPanelForm(controlpanel.RegistryEditForm):

    id = "NavigationControlPanel"
    label = _("Navigation Settings")
    description = _(
        "Lets you control how navigation is constructed in your site. " +
        "Note that to control how the navigation tree is displayed, you " +
        "should go to 'Manage portlets' at the root of the site (or " +
        "wherever a navigation tree portlet has been added) and change " +
        "its settings directly.")
    schema = INavigationSchema
    schema_prefix = "plone"

    def updateFields(self):
        super().updateFields()
        self.fields['displayed_types'].widgetFactory = \
            CheckBoxFieldWidget
        self.fields['workflow_states_to_show'].widgetFactory = \
            CheckBoxFieldWidget


class NavigationControlPanel(controlpanel.ControlPanelFormWrapper):
    form = NavigationControlPanelForm
