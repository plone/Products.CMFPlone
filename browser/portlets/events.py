from zope.component import getView
from zope.interface import implements

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IEventsPortlet


class EventsPortlet(utils.BrowserView):
    implements(IEventsPortlet)
