# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ISiteSchema
from plone.app.registry.browser import controlpanel
from plone.formwidget.namedfile.widget import NamedImageFieldWidget
from z3c.form import interfaces


class SiteControlPanelForm(controlpanel.RegistryEditForm):

    id = "SiteControlPanel"
    label = _(u"Site Settings")
    description = _("Site-wide settings.")
    schema = ISiteSchema
    schema_prefix = "plone"

    def updateFields(self):
        super(SiteControlPanelForm, self).updateFields()
        self.fields['site_logo'].widgetFactory = NamedImageFieldWidget

    def updateWidgets(self):
        super(SiteControlPanelForm, self).updateWidgets()
        # hide the default_page field/widgets
        self.widgets['default_page'].mode = interfaces.HIDDEN_MODE


class SiteControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SiteControlPanelForm
