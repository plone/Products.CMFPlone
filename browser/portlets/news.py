import zope.deprecation
from zope.interface import implements
from zope.component import getUtility

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INewsPortlet
from Products.CMFCore.interfaces import ICatalogTool
from Products.CMFCore.interfaces import IURLTool


class NewsPortlet(utils.BrowserView):
    implements(INewsPortlet)

    def published_news_items(self):
        context = utils.context(self)
        portal_catalog = getUtility(ICatalogTool)

        return self.request.get('news', 
                        portal_catalog.searchResults(portal_type='News Item',
                                                     sort_on='Date',
                                                     sort_order='reverse',
                                                     review_state='published'))
    def all_news_link(self):
        context = utils.context(self)
        utool = getUtility(IURLTool)
        portal_url = utool()
        portal = utool.getPortalObject()

        if 'news' in portal.objectIds():
            return '%s/news' % portal_url
        else:
            return '%s/news_listing' % portal_url

zope.deprecation.deprecated(
  ('NewsPortlet', ),
   "Plone's portlets are based on plone.app.portlets now. The old portlets "
   "will be removed in Plone 3.5."
  )
