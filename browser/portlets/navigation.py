
from Products.CMFPlone.browser.interfaces import INavigationPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView
from Products import CMFPlone

class NavigationPortlet(BrowserView):
    implements(INavigationPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def includeTop(self):
        g = getView(self.context, 'globals_view', self.request)
        return g.portal_properties().navtree_properties.includeTop

    def createNavTree(self):
        data = self.context.plone_utils.createNavTree(self.context, sitemap=None)
        return self.context.portlet_navtree_macro(children=data.get('children', []),
                                                  level=1, show_children=True, isNaviTree=True)

    def isDefaultorPortalorPortalChild(self):
        """ feel the hacking love """
        g = getView(self.context, 'globals_view', self.request)
        portal = g.portal()
        return portal == self.context or (portal == self.context.getParentNode() and
                                          self.context.plone_utils.isDefaultPage(self.context))        



