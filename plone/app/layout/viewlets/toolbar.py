# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import PersonalBarViewlet
from plone.app.viewletmanager.manager import OrderedViewletManager
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from zope.component import getUtility

import json


class ToolbarViewletManager(OrderedViewletManager):
    custom_template = ViewPageTemplateFile('toolbar.pt')

    def base_render(self):
        return super(ToolbarViewletManager, self).render()

    def render(self):
        return self.custom_template()

    @property
    @memoize
    def context_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_context_state'
        )

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter(
            (self.context, self.request),
            name='plone_portal_state'
        )

    def get_options(self):
        registry = getUtility(IRegistry)
        options = {}

        lessvars = registry.get('plone.lessvariables', {})

        toolbar_width = lessvars.get('plone-left-toolbar-expanded', None)
        submenu_width = lessvars.get('plone-toolbar-submenu-width', None)
        desktop_width = lessvars.get('plone-screen-sm-min', None)

        if toolbar_width:
            options['toolbar_width'] = toolbar_width
        if submenu_width:
            options['submenu_width'] = submenu_width
        if desktop_width:
            options['desktop_width'] = desktop_width

        return json.dumps(options)

    def get_personal_bar(self):
        viewlet = PersonalBarViewlet(
            self.context,
            self.request,
            self.__parent__, self
        )
        viewlet.update()
        return viewlet

    def get_toolbar_logo(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISiteSchema, prefix='plone', check=False)
        portal_url = self.portal_state.portal_url()
        try:
            logo = settings.toolbar_logo
        except AttributeError:
            logo = '/++plone++static/plone-toolbarlogo.svg'
        if not logo:
            logo = '/++plone++static/plone-toolbarlogo.svg'
        return portal_url + logo

    def show_switcher(self):
        return False
