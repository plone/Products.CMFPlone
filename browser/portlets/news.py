from zope.component import getView
from zope.interface import implements

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INewsPortlet


class NewsPortlet(utils.BrowserView):
    implements(INewsPortlet)

    def news(self):
        g = getView(self.context, 'globals_view', self.request)
        return g.utool()() + '/news'

    def news_listing(self):
        g = getView(self.context, 'globals_view', self.request)
        return g.utool()() + '/news_listing'
