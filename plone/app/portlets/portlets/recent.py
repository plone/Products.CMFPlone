from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

class IRecentPortlet(IPortletDataProvider):

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list'),
                       required=True,
                       default=5)

class Assignment(base.Assignment):
    implements(IRecentPortlet)

    def __init__(self, count=5):
        self.count = count

    @property
    def title(self):
        return _(u"Recent items")

class Renderer(base.Renderer):

    render = ViewPageTemplateFile('recent.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        
    @property
    def available(self):
        return not self.anonymous and len(self._data())

    def recent_items(self):
        return self._data()

    def recently_modified_link(self):
        return '%s/recently_modified' % self.portal_url

    @memoize
    def _data(self):
        limit = self.data.count
        return self.catalog(portal_type=self.typesToShow,
                            sort_on='modified',
                            sort_order='reverse',
                            sort_limit=limit)[:limit]


class AddForm(base.AddForm):
    form_fields = form.Fields(IRecentPortlet)
    label = _(u"Add Recent portlet")
    description = _(u"This portlet displays recently modified content.")

    def create(self, data):
        return Assignment(count=data.get('count', 5))

class EditForm(base.EditForm):
    form_fields = form.Fields(IRecentPortlet)
    label = _(u"Edit Recent portlet")
    description = _(u"This portlet displays recently modified content.")
