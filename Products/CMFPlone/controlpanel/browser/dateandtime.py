from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IDateAndTimeSchema


class DateAndTimeControlPanelForm(RegistryEditForm):
    id = "DateAndTimeControlPanel"
    schema = IDateAndTimeSchema
    schema_prefix = "plone"

    label = _("label_dateandtime_settings", default="Date and Time Settings")
    description = _(
        "help_event_settings",
        default="Date and Time related settings like timezone(s), etc.",
    )


class DateAndTimeControlPanel(ControlPanelFormWrapper):
    form = DateAndTimeControlPanelForm
