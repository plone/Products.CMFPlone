# -*- coding: utf-8 -*-
from plone.app.registry.browser import controlpanel
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import ISocialMediaSchema


class SocialControlPanelForm(controlpanel.RegistryEditForm):

    id = 'SocialControlPanel'
    label = _(u'Social Media Settings')
    description = _('Social media sharing settings.')
    schema = ISocialMediaSchema
    schema_prefix = 'plone'


class SocialControlPanel(controlpanel.ControlPanelFormWrapper):
    form = SocialControlPanelForm
