from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from Products.CMFPlone.browser.interfaces import ISitemapView


class SitemapView(BrowserView):
    implements(ISitemapView)

    def createSiteMap(self):
        context = aq_inner(self.context)
        view = getMultiAdapter((context, self.request),
                               name='sitemap_builder_view')
        data = view.siteMap()
        properties = getToolByName(context, 'portal_properties')
        navtree_properties = getattr(properties, 'navtree_properties')
        bottomLevel = navtree_properties.getProperty('bottomLevel', 0)
        # XXX: The recursion should probably be done in python code
        return context.portlet_navtree_macro(children=data.get('children', []),
                                             level=1, bottomLevel=bottomLevel)
