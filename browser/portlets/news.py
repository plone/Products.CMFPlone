from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INewsPortlet


class NewsPortlet(utils.BrowserView):
    implements(INewsPortlet)

    def published_news_items(self):
        context = utils.context(self)
        portal_catalog = getToolByName(context, 'portal_catalog')

        return self.request.get('news', 
                                portal_catalog.searchResults(portal_type='News Item',
                                                             sort_on='Date',
                                                             sort_order='reverse',
                                                             review_state='published'))
    def all_news_link(self):
        context = utils.context(self)
        utool = getToolByName(context, 'portal_url')
        portal_url = utool()
        portal = utool.getPortalObject()

        if 'news' in portal.contentIds():
            return '%s/news' % portal_url
        else:
            return '%s/news_listing' % portal_url
