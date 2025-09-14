from plone.app.registry.browser import controlpanel
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import ISocialMediaSchema


class SocialControlPanelForm(controlpanel.RegistryEditForm):
    id = "SocialControlPanel"
    label = _("Social Media Settings")
    description = _("Social media sharing settings.")
    schema = ISocialMediaSchema
    schema_prefix = "plone"


class SocialControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SocialControlPanelForm
