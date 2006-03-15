from zope.component import getView
from zope.interface import implements

from Acquisition import aq_base, aq_inner, aq_parent

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationPortlet

from Products.CMFPlone.browser.navtree import getNavigationRoot

class NavigationPortlet(utils.BrowserView):
    implements(INavigationPortlet)

    def title(self):
        context = utils.context(self)
        portal_properties = getToolByName(context, 'portal_properties')
        return portal_properties.navtree_properties.name

    def display(self):
        tree = self.getNavTree()
        return len(tree['children']) > 0
        
    def includeTop(self):
        context = utils.context(self)
        portal_properties = getToolByName(context, 'portal_properties')
        return portal_properties.navtree_properties.includeTop

    def navigationRoot(self):
        context = utils.context(self)
        portal_properties = getToolByName(context, 'portal_properties')
        portal_url = getToolByName(context, 'portal_url')
        
        topLevel = portal_properties.navtree_properties.topLevel
        rootPath = getNavigationRoot(context, topLevel = topLevel)
        
        return portal_url.getPortalObject().restrictedTraverse(rootPath) 

    def rootTypeName(self):
        context = utils.context(self)
        root = self.navigationRoot()
        return utils.normalizeString(root.portal_type, context=context)

    def createNavTree(self):
        context = utils.context(self)
        data = self.getNavTree()
        properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        bottomLevel = navtree_properties.getProperty('bottomLevel', 0)
        # XXX: The recursion should probably be done in python code
        return context.portlet_navtree_macro(
            children=data.get('children', []),
            level=1, show_children=True, isNaviTree=True, bottomLevel=bottomLevel)

    def isPortalOrDefaultChild(self):
        context = utils.context(self)
        utool = getToolByName(context, 'portal_url')
        portal = utool.getPortalObject()
        return (aq_base(portal) == aq_base(context) or
                (aq_base(portal) == aq_base(aq_parent(aq_inner(context))) and
                utils.isDefaultPage(context, self.request, context)))

    def getNavTree(self):
        """Calculate the navtree"""
        tree = getattr(self, '_navtree', None)
        if tree is not None:
            return tree
        else:
            context = utils.context(self)
            view = getView(context, 'navtree_builder_view', self.request)
            self._navtree = view.navigationTree()
            return self._navtree