from zope.interface import implements
from zope.component import getMultiAdapter
from plone.memoize.view import memoize, memoize_contextless

from Products.Five.browser import BrowserView

from Products.CMFPlone.browser.navtree import getNavigationRoot

from interfaces import IPortalState

class PortalState(BrowserView):
    """Information about the state of the portal
    """
    
    implements(IPortalState)
    
    @property
    @memoize_contextless
    def portal(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_url.getPortalObject()
    
    @property
    @memoize_contextless
    def portal_title(self):
        return self.portal.Title()
        
    @property
    @memoize_contextless
    def portal_url(self):
        return self.portal.absolute_url()
        
    @property
    @memoize_contextless
    def navigation_root_url(self):
        portal = self.portal
        portalPath = '/'.join(portal.getPhysicalPath())

        rootPath = getNavigationRoot(self.context)
        rootSubPath = rootPath[len(portalPath):]

        return portal.absolute_url() + rootSubPath
    
    @property
    @memoize_contextless
    def default_language(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        site_properties = tools.portal_properties.site_properties
        return site_properties.getProperty('default_lanaguage', None)
    
    @property
    @memoize
    def language(self):
        return self.request.get('language', None) or self.context.Language() or \
                self.default_language
        
    @property
    @memoize
    def is_rtl(self):
        try:
            from Products.PlacelessTranslationService import isRTL
        except ImportError:
            # This may mean we have an old version of PTS or no PTS at all.
            return False
        else:
            try:
                return isRTL(self.context, 'plone')
            except AttributeError:
                # This may mean that PTS is present but not installed.
                # Can effectively only happen in unit tests.
                return False
                
    @property
    @memoize_contextless
    def member(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_membership.getAuthenticatedMember()
        
    @property
    @memoize_contextless
    def anonymous(self):
        tools = getMultiAdapter((self.context, self.request), name='plone_tools')
        return tools.portal_membership.isAnonymousUser()
    