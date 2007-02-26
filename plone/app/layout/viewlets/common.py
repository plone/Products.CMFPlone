from zope.interface import implements
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewlet

from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView


class ViewletBase(BrowserView):
    """ Base class with common functions for link viewlets.
    """
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(ViewletBase, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        self.portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.portal_url = self.portal_state.portal_url()

    def update(self):
        pass

    def render(self):
        raise NotImplementedError(
            '`render` method must be implemented by subclass.')


class TitleViewlet(ViewletBase):

    def __init__(self, context, request, view, manager):
        super(TitleViewlet, self).__init__(context, request, view, manager)
        self.context_state = getMultiAdapter((context, request), name=u'plone_context_state')
        self.page_title = self.context_state.object_title
        self.portal_title = self.portal_state.portal_title

    def render(self):
        return u"<title>%s &mdash; %s</title>" % (
            safe_unicode(self.page_title()),
            safe_unicode(self.portal_title()))
