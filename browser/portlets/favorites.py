
from Products.CMFPlone.browser.interfaces import IFavoritesPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView

class FavoritesPortlet(BrowserView):
    implements(IFavoritesPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request

