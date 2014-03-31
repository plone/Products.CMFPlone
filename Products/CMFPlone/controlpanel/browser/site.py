from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ISiteSchema
from plone.app.registry.browser import controlpanel


class SiteControlPanelForm(controlpanel.RegistryEditForm):

    id = "SiteControlPanel"
    label = _(u"Site settings")
    description = _("Site-wide settings.")
    schema = ISiteSchema
    schema_prefix = "plone"


class SiteControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SiteControlPanelForm
