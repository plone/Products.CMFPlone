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

class IReviewPortlet(IPortletDataProvider):
    
    pass

class Assignment(base.Assignment):
    implements(IReviewPortlet)

    @property
    def title(self):
        return _(u"Review list")

class Renderer(base.Renderer):

    render = ViewPageTemplateFile('review.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()

        plone_tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')
        self.workflow = plone_tools.workflow()

    @property
    def available(self):
        return not self.anonymous and len(self._data())

    def review_items(self):
        return self._data()

    def full_review_link(self):
        return '%s/full_review_list' % self.portal_url

    @memoize
    def _data(self):
        if self.anonymous:
            return []

        return self.workflow.getWorklistsResults()


class AddForm(base.NullAddForm):
    form_fields = form.Fields(IReviewPortlet)
    label = _(u"Add Review Portlet")
    description = _(u"This portlet displays a queue of documents awaiting review.")

    def create(self):
        return Assignment()
