from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

class INewsPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list'),
                       required=True,
                       default=5)

class Assignment(base.Assignment):
    implements(INewsPortlet)

    def __init__(self, count=5):
        self.count = 5

    @property
    def title(self):
        return _(u"News portlet")

class Renderer(base.Renderer):

    render = ZopeTwoPageTemplateFile('news.pt')

    def show(self):
        return len(self._data())

    def published_news_items(self):
        return self._data()

    def all_news_link(self):
        context = aq_inner(self.context)
        utool = getToolByName(context, 'portal_url')
        portal_url = utool()
        portal = utool.getPortalObject()

        if 'news' in portal.objectIds():
            return '%s/news' % portal_url
        else:
            return '%s/news_listing' % portal_url

    def _data(self):
        data = getattr(self, '__results', None)
        if data is None:
            context = aq_inner(self.context)
            catalog = getToolByName(context, 'portal_catalog')
            limit = self.data.count
            self.__results = catalog(portal_type='News Item',
                                     review_state='published',
                                     sort_on='Date',
                                     sort_order='reverse',
                                     sort_limit=limit)[:limit]
        return self.__results

class AddForm(base.AddForm):
    form_fields = form.Fields(INewsPortlet)

    def create(self, data):
        return Assignment(count=data.get('count', 5))

class EditForm(base.EditForm):
    form_fields = form.Fields(INewsPortlet)