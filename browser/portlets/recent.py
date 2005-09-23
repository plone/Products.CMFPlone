
from Products.CMFPlone.browser.interfaces import IRecentPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView

class RecentPortlet(BrowserView):
    implements(IRecentPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request


