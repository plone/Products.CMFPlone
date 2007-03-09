from zope.component import getUtility
from zope.interface import implements
from plone.memoize.view import memoize_contextless

from Products.Five.browser import BrowserView
from Products.CMFCore.interfaces import IActionsTool
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IMembershipTool
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import ISyndicationTool
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IURLTool
from Products.CMFCore.interfaces import IConfigurableWorkflowTool
from Products.CMFPlone.interfaces import IInterfaceTool

from interfaces import ITools

class Tools(BrowserView):
    """Common tools
    """
    
    implements(ITools)
    
    @memoize_contextless
    def actions(self):
        return getUtility(IActionsTool)
        
    @memoize_contextless
    def catalog(self):
        return getUtility(ICatalogTool)
        
    @memoize_contextless
    def interface(self):
        return getUtility(IInterfaceTool)
        
    @memoize_contextless
    def membership(self):
        return getUtility(IMembershipTool)
        
    @memoize_contextless
    def properties(self):
        return getUtility(IPropertiesTool)

    @memoize_contextless
    def syndication(self):
        return getUtility(ISyndicationTool)
        
    @memoize_contextless
    def url(self):
        return getUtility(IURLTool)
        
    @memoize_contextless
    def types(self):
        return getUtility(ITypesTool)

    @memoize_contextless
    def workflow(self):
        return getUtility(IConfigurableWorkflowTool)
