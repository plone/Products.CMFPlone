import zope.deprecation
from plone.i18n.normalizer.interfaces import IIDNormalizer

from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implements

from Acquisition import aq_base, aq_inner, aq_parent
from Products.Five import BrowserView

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationPortlet

class NavigationPortlet(BrowserView):
    implements(INavigationPortlet)

    def title(self):
        context = aq_inner(self.context)
        portal_properties = getToolByName(context, 'portal_properties')
        return portal_properties.navtree_properties.name

    def display(self):
        tree = self.getNavTree()
        root = self.getNavRoot()
        return (root is not None and len(tree['children']) > 0)

    def includeTop(self):
        context = aq_inner(self.context)
        portal_properties = getToolByName(context, 'portal_properties')
        return portal_properties.navtree_properties.includeTop

    def navigationRoot(self):
        return self.getNavRoot()

    def rootTypeName(self):
        root = self.getNavRoot()
        return queryUtility(IIDNormalizer).normalize(root.portal_type)

    def createNavTree(self):
        context = aq_inner(self.context)
        data = self.getNavTree()
        properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        bottomLevel = navtree_properties.getProperty('bottomLevel', 0)
        return context.portlet_navtree_macro(
            children=data.get('children', []),
            level=1, show_children=True, isNaviTree=True, bottomLevel=bottomLevel)

    def isPortalOrDefaultChild(self):
        context = aq_inner(self.context)
        root = self.getNavRoot()
        return (aq_base(root) == aq_base(context) or
                (aq_base(root) == aq_base(aq_parent(aq_inner(context))) and
                utils.isDefaultPage(context, self.request, context)))

    # Cached lookups

    def getNavRoot(self):
        """Get and cache the navigation root"""
        if not utils.base_hasattr(self, '_root'):
            context = aq_inner(self.context)
            portal_url = getToolByName(context, 'portal_url')
            portal = portal_url.getPortalObject()

            view = getMultiAdapter((context, self.request),
                                   name='navtree_builder_view')
            rootPath = view.navigationTreeRootPath()

            if rootPath == portal_url.getPortalPath():
                root = portal
            else:
                try:
                    root = portal.unrestrictedTraverse(rootPath)
                except (AttributeError, KeyError,):
                    root = portal

            self._root = [root]

        return self._root[0]

    def getNavTree(self):
        """Calculate the navtree"""
        tree = getattr(self, '_navtree', None)
        if tree is not None:
            return tree
        else:
            context = aq_inner(self.context)
            view = getMultiAdapter((context, self.request),
                                   name='navtree_builder_view')
            self._navtree = view.navigationTree()
            return self._navtree

zope.deprecation.deprecated(
  ('NavigationPortlet', ),
   "Plone's portlets are based on plone.app.portlets now. The old portlets "
   "will be removed in Plone 4.0."
  )
