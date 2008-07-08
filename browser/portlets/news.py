from Acquisition import aq_inner
import zope.deprecation
from zope.interface import implements

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.interfaces import INewsPortlet


class NewsPortlet(BrowserView):
    implements(INewsPortlet)

    def published_news_items(self):
        context = aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')

        return self.request.get('news', 
                                portal_catalog.searchResults(portal_type='News Item',
                                                             sort_on='Date',
                                                             sort_order='reverse',
                                                             review_state='published'))
    def all_news_link(self):
        context = aq_inner(self.context)
        utool = getToolByName(context, 'portal_url')
        portal_url = utool()
        portal = utool.getPortalObject()

        if 'news' in portal.objectIds():
            return '%s/news' % portal_url
        else:
            return '%s/news_listing' % portal_url

zope.deprecation.deprecated(
  ('NewsPortlet', ),
   "Plone's portlets are based on plone.app.portlets now. The old portlets "
   "will be removed in Plone 4.0."
  )
