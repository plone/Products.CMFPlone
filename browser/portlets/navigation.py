from zope.component import getView
from zope.interface import implements

from Acquisition import aq_base, aq_inner, aq_parent

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationPortlet


class NavigationPortlet(utils.BrowserView):
    implements(INavigationPortlet)

    def includeTop(self):
        context = utils.context(self)
        portal_properties = getToolByName(context, 'portal_properties')
        return portal_properties.navtree_properties.includeTop

    def createNavTree(self):
        context = utils.context(self)
        view = getView(context, 'nav_view', self.request)
        data = view.navigationTree()
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
