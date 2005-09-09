
from Products.CMFPlone.browser.interfaces import INewsPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView
from Products import CMFPlone

class NewsPortlet(BrowserView):
    implements(INewsPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def news(self):
        g = getView(self.context, 'globals_view', self.request)
        return g.utool()() + '/news'

    def news_listing(self):
        g = getView(self.context, 'globals_view', self.request)
        return g.utool()() + '/news_listing'

