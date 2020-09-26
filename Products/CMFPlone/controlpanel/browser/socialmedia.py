from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ISocialMediaSchema
from plone.app.registry.browser import controlpanel


class SocialControlPanelForm(controlpanel.RegistryEditForm):

    id = "SocialControlPanel"
    label = _("Social Media Settings")
    description = _("Social media sharing settings.")
    schema = ISocialMediaSchema
    schema_prefix = "plone"


class SocialControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SocialControlPanelForm
