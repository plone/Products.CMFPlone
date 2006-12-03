from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from DateTime.DateTime import DateTime
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

class IEventsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list'),
                       required=True,
                       default=5)

class Assignment(base.Assignment):
    implements(IEventsPortlet)

    def __init__(self, count=5):
        self.count = 5

    @property
    def title(self):
        return _(u"Events portlet")

class Renderer(base.Renderer):

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        
        utool = getToolByName(self.context, 'portal_url')
        self.portal_url = utool()
        self.portal = utool.getPortalObject()
        
        self.have_events_folder = 'events' in self.portal.objectIds()

    render = ZopeTwoPageTemplateFile('events.pt')

    def show(self):
        return len(self._data())

    def published_events(self):
        return self._data()

    def all_events_link(self):
        if self.have_events_folder:
            return '%s/events' % self.portal_url
        else:
            return '%s/events_listing' % self.portal_url

    def prev_events_link(self):
        if self.have_events_folder and 'previous' in self.portal['events'].objectIds():
            return '%s/events/previous' % self.portal_url
        else:
            return None

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        limit = self.data.count
        return catalog(portal_type='Event',
                       review_state='published',
                       end={'query': DateTime(),
                            'range': 'min'},
                       sort_on='start',
                       sort_limit=limit)[:limit]

class AddForm(base.AddForm):
    form_fields = form.Fields(IEventsPortlet)

    def create(self, data):
        return Assignment(count=data.get('count', 5))

class EditForm(base.EditForm):
    form_fields = form.Fields(IEventsPortlet)