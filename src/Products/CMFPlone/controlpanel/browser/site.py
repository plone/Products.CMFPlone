from plone.app.registry.browser import controlpanel
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import ISiteSchema
from plone.formwidget.namedfile.widget import NamedImageFieldWidget
from z3c.form import interfaces


class SiteControlPanelForm(controlpanel.RegistryEditForm):
    id = "SiteControlPanel"
    label = _("Site Settings")
    description = _("Site-wide settings.")
    schema = ISiteSchema
    schema_prefix = "plone"

    def updateFields(self):
        super().updateFields()
        self.fields["site_logo"].widgetFactory = NamedImageFieldWidget
        self.fields["site_favicon"].widgetFactory = NamedImageFieldWidget

    def updateWidgets(self):
        super().updateWidgets()
        # hide the default_page field/widgets
        self.widgets["default_page"].mode = interfaces.HIDDEN_MODE


class SiteControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SiteControlPanelForm
