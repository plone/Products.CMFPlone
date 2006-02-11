from zope.interface import implements
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IEventsPortlet


class EventsPortlet(utils.BrowserView):
    implements(IEventsPortlet)

    def __init__(self, context, request, *args, **kw):
        super(EventsPortlet, self).__init__(context, request, *args, **kw)
        utool = getToolByName(context, 'portal_url')
        self.portal_url = utool()
        # this has a messed up context, but we don't care in this case
        self.portal = utool.getPortalObject()


    def published_events(self):
        context = utils.context(self)
        portal_catalog = getToolByName(context, 'portal_catalog')

        return portal_catalog.searchResults(portal_type='Event',
                                            end={'query': DateTime(),
                                                 'range': 'min'},
                                            sort_on='start',
                                            sort_limit=5,
                                            review_state='published')[:5]

    def all_events_link(self):
        if 'events' in self.portal.contentIds():
            return '%s/events' % self.portal_url
        else:
            return '%s/events_listing' % self.portal_url

    def prev_events_link(self):
        if 'events' in self.portal.contentIds() and \
           'previous' in self.portal.events.contentIds():
            return '%s/news/previous' % self.portal_url
        else:
            return None