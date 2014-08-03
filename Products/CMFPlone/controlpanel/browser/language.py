# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.registry.browser import controlpanel

from Products.CMFPlone.interfaces import ILanguageSchema


class LanguageControlPanelForm(controlpanel.RegistryEditForm):

    id = "LanguageControlPanel"
    label = _(u"heading_language_settings", default="Language Settings")
    description = _(u"description_language_settings",
                    default="Settings related to interface languages and "
                            "content translations.")

    schema = ILanguageSchema
    schema_prefix = "plone"


class LanguageControlPanel(controlpanel.ControlPanelFormWrapper):
    form = LanguageControlPanelForm



#class LanguageControlPanel(ControlPanelForm):
#    form_fields = FormFields(ILanguageSchema)
#    form_fields['default_language'].custom_widget = \
#       LanguageDropdownChoiceWidget
#
#    form_name = _(u"heading_language_settings", default="Language Settings")
