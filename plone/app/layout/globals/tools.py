from Acquisition import aq_inner

from zope.interface import implements
from plone.memoize.view import memoize_contextless

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from interfaces import ITools

class Tools(BrowserView):
    """Common tools
    """
    
    implements(ITools)
    
    @memoize_contextless
    def actions(self):
        return getToolByName(aq_inner(self.context), 'portal_actions')
        
    @memoize_contextless
    def catalog(self):
        return getToolByName(aq_inner(self.context), 'portal_catalog')
        
    @memoize_contextless
    def interface(self):
        return getToolByName(aq_inner(self.context), 'portal_interface')
        
    @memoize_contextless
    def membership(self):
        return getToolByName(aq_inner(self.context), 'portal_membership')
        
    @memoize_contextless
    def properties(self):
        return getToolByName(aq_inner(self.context), 'portal_properties')

    @memoize_contextless
    def syndication(self):
        return getToolByName(aq_inner(self.context), 'portal_syndication')
        
    @memoize_contextless
    def url(self):
        return getToolByName(aq_inner(self.context), 'portal_url')
        
    @memoize_contextless
    def types(self):
        return getToolByName(aq_inner(self.context), 'portal_types')

    @memoize_contextless
    def workflow(self):
        return getToolByName(aq_inner(self.context), 'portal_workflow')
