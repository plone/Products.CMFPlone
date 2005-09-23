
from Products.CMFPlone.browser.interfaces import IEventsPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView

class EventsPortlet(BrowserView):
    implements(IEventsPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request

