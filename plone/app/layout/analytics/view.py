from zope.component import getUtility
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from plone.memoize import view, instance

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.interfaces import IPropertiesTool
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile


class AnalyticsViewlet(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(BrowserView, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        pass

    def render(self):
        """render the webstats snippet"""
        ptool = getUtility(IPropertiesTool)
        snippet = ptool.site_properties.webstats_js
        return snippet
