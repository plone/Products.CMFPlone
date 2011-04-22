from zope.interface import implements

from plone.memoize.view import memoize_contextless
from plone.memoize.view import memoize

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.navigation.root import getNavigationRootObject


from interfaces import IPortalState

RIGHT_TO_LEFT = ['ar', 'fa', 'he', 'ps']


class PortalState(BrowserView):
    """Information about the state of the portal
    """
    implements(IPortalState)

    @memoize_contextless
    def portal(self):
        context = aq_inner(self.context)
        return getToolByName(context, 'portal_url').getPortalObject()

    @memoize_contextless
    def portal_title(self):
        return self.portal().Title()

    @memoize_contextless
    def portal_url(self):
        return self.portal().absolute_url()

    @memoize
    def navigation_root(self):
        context = aq_inner(self.context)
        portal = self.portal()
        return getNavigationRootObject(context, portal)

    @memoize
    def navigation_root_title(self):
        title = self.navigation_root().Title
        if callable(title):
            return title()
        else:
            return title

    @memoize
    def navigation_root_path(self):
        return getNavigationRoot(aq_inner(self.context))

    @memoize
    def navigation_root_url(self):
        rootPath = self.navigation_root_path()
        return self.request.physicalPathToURL(rootPath)

    @memoize_contextless
    def default_language(self):
        context = aq_inner(self.context)
        site_properties = getToolByName(context, "portal_properties").site_properties
        return site_properties.getProperty('default_language', None)

    def language(self):
        return self.request.get('LANGUAGE', None) or \
                aq_inner(self.context).Language() or self.default_language()

    def locale(self):
        return self.request.locale

    def is_rtl(self):
        language = self.language()
        if not language:
            return False
        if language[:2] in RIGHT_TO_LEFT:
            return True
        return False

    @memoize_contextless
    def member(self):
        context = aq_inner(self.context)
        tool = getToolByName(context, "portal_membership")
        return tool.getAuthenticatedMember()

    @memoize_contextless
    def anonymous(self):
        context = aq_inner(self.context)
        tool = getToolByName(context, "portal_membership")
        return bool(tool.isAnonymousUser())

    @memoize_contextless
    def friendly_types(self):
        context = aq_inner(self.context)
        site_properties = getToolByName(context, "portal_properties").site_properties
        not_searched = site_properties.getProperty('types_not_searched', [])

        types = getToolByName(context, "portal_types").listContentTypes()
        return [t for t in types if t not in not_searched]
