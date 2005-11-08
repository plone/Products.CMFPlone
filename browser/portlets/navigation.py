from zope.component import getView
from zope.interface import implements

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationPortlet


class NavigationPortlet(utils.BrowserView):
    implements(INavigationPortlet)

    def includeTop(self):
        context = utils.context(self)
        g = getView(context, 'plone', self.request)
        return g.portal_properties().navtree_properties.includeTop

    def createNavTree(self):
        context = utils.context(self)
        data = context.plone_utils.createNavTree(context, sitemap=None)
        return context.portlet_navtree_macro(
            children=data.get('children', []),
            level=1, show_children=True, isNaviTree=True)

    def isPortalOrDefaultChild(self):
        """ feel the hacking love """
        context = utils.context(self)
        g = getView(context, 'plone', self.request)
        portal = g.portal()
        return (portal == context or
                (portal == context.getParentNode() and
                 context.plone_utils.isDefaultPage(context)))
