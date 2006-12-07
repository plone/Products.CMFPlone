from zope.interface import implements
from zope.component import getMultiAdapter

from plone.memoize.view import memoize, memoize_contextless

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from plone.app.layout.navigation.root import getNavigationRoot

from interfaces import IPortalState

class PortalState(BrowserView):
    """Information about the state of the portal
    """
    
    implements(IPortalState)
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self._context = [context]
    
    @memoize_contextless
    def portal(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.url().getPortalObject()
    
    @memoize_contextless
    def portal_title(self):
        return self.portal().Title()
        
    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()
        
    @memoize_contextless
    def navigation_root_path(self):
        return getNavigationRoot(aq_inner(self.context))
    
    @memoize_contextless
    def navigation_root_url(self):
        portal = self.portal()
        portalPath = '/'.join(portal.getPhysicalPath())

        rootPath = self.navigation_root_path()
        rootSubPath = rootPath[len(portalPath):]

        return portal.absolute_url() + rootSubPath
    
    @memoize_contextless
    def default_language(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        site_properties = tools.properties().site_properties
        return site_properties.getProperty('default_language', None)
    
    @memoize
    def language(self):
        return self.request.get('language', None) or \
                aq_inner(self.context).Language() or self.default_language
        
    @memoize
    def is_rtl(self, domain='plone'):
        try:
            from Products.PlacelessTranslationService import isRTL
        except ImportError:
            # This may mean we have an old version of PTS or no PTS at all.
            return False
        else:
            try:
                return isRTL(aq_inner(self.context), domain)
            except AttributeError:
                # This may mean that PTS is present but not installed.
                # Can effectively only happen in unit tests.
                return False
                
    @memoize_contextless
    def member(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.membership().getAuthenticatedMember()
        
    @memoize_contextless
    def anonymous(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return bool(tools.membership().isAnonymousUser())
    
    @memoize_contextless
    def friendly_types(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        properties = tools.properties()
        
        site_properties = getattr(properties, 'site_properties')
        not_searched = site_properties.getProperty('types_not_searched', [])

        portal_types = tools.types()
        types = portal_types.listContentTypes()

        return [t for t in types if t not in not_searched]