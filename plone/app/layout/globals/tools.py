# -*- coding: utf-8 -*-
from interfaces import ITools
from plone.memoize.view import memoize_contextless
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.interface import implementer


@implementer(ITools)
class Tools(BrowserView):
    """Common tools
    """

    @memoize_contextless
    def actions(self):
        return getToolByName(self.context, 'portal_actions')

    @memoize_contextless
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @memoize_contextless
    def membership(self):
        return getToolByName(self.context, 'portal_membership')

    @memoize_contextless
    def properties(self):
        return getToolByName(self.context, 'portal_properties')

    @memoize_contextless
    def url(self):
        return getToolByName(self.context, 'portal_url')

    @memoize_contextless
    def types(self):
        return getToolByName(self.context, 'portal_types')

    @memoize_contextless
    def workflow(self):
        return getToolByName(self.context, 'portal_workflow')
