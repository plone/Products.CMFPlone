from zope.component import getView
from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import ISitemapView


class SitemapView(utils.BrowserView):
    implements(ISitemapView)

    def createSitemap(self):
        context = utils.context(self)
        view = getView(context, 'nav_view', self.request)
        data = view.siteMap()
        properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        bottomLevel = navtree_properties.getProperty('bottomLevel', 0)
        # XXX: The recursion should probably be done in python code
        return context.portlet_navtree_macro(
            children=data.get('children', []),
            level=1, show_children=True, isNaviTree=True, bottomLevel=bottomLevel)
