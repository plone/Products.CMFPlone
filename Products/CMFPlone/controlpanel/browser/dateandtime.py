# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IDateAndTimeSchema
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm


class DateAndTimeControlPanelForm(RegistryEditForm):

    id = "DateAndTimeControlPanel"
    schema = IDateAndTimeSchema
    schema_prefix = "plone"

    label = _(u"label_dateandtime_settings", default=u"Date and Time Settings")
    description = _(
        u"help_event_settings",
        default=u"Date and Time related settings like timezone(s), etc."
    )


class DateAndTimeControlPanel(ControlPanelFormWrapper):
    form = DateAndTimeControlPanelForm
