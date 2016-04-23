# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISiteSchema
from Products.Five.browser import BrowserView
from zope.component import getUtility
from zope.interface import implementer
from zope.viewlet.interfaces import IViewlet


@implementer(IViewlet)
class AnalyticsViewlet(BrowserView):

    def __init__(self, context, request, view, manager):
        super(AnalyticsViewlet, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        pass

    def render(self):
        """render the webstats snippet"""
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)
        try:
            if site_settings.webstats_js:
                return site_settings.webstats_js
        except AttributeError:
            pass
        return ''
