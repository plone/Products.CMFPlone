from zope.component import getMultiAdapter
from zope.interface import implements

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import ISitemapView


class SitemapView(utils.BrowserView):
    implements(ISitemapView)

    def createSitemap(self):
        context = utils.context(self)
        view = getMultiAdapter((context, self.request), name='nav_view')
        data = view.navigationTree(sitemap=True)
        # XXX: The recursion should probably be done in python code
        return context.portlet_navtree_macro(
            children=data.get('children', []),
            level=1, show_children=True, isNaviTree=True)
