from zope.interface import implements
from plone.memoize.view import memoize_contextless

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName

from interfaces import ITools

class Tools(BrowserView):
    """Common tools
    """
    
    implements(ITools)
    
    @property
    @memoize_contextless
    def portal_actions(self):
        return getToolByName(self.context, 'portal_actions')
        
    @property
    @memoize_contextless
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')
        
    @property
    @memoize_contextless
    def portal_interface(self):
        return getToolByName(self.context, 'portal_interface')
        
    @property
    @memoize_contextless
    def portal_membership(self):
        return getToolByName(self.context, 'portal_membership')
        
    @property
    @memoize_contextless
    def portal_properties(self):
        return getToolByName(self.context, 'portal_properties')

    @property
    @memoize_contextless
    def portal_syndication(self):
        return getToolByName(self.context, 'portal_syndication')
        
    @property
    @memoize_contextless
    def portal_url(self):
        return getToolByName(self.context, 'portal_url')

    @property
    @memoize_contextless
    def portal_workflow(self):
        return getToolByName(self.context, 'portal_workflow')

    @property
    @memoize_contextless
    def plone_utils(self):
        return getToolByName(self.context, 'plone_utils')