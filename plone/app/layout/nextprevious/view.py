from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.memoize import view, instance

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner, aq_parent


class NextPreviousView(BrowserView):
    """Information about next/previous navigation
    """

    @view.memoize
    def next(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getNextItem(aq_inner(self.context))
    
    @view.memoize
    def previous(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getPreviousItem(aq_inner(self.context))

    @view.memoize
    def enabled(self):
        provider = self._provider()
        if provider is None:
            return False
        return provider.enabled

    @instance.memoize
    def _provider(self):
        # Note - the next/previous provider is the container of this object!
        # This may not support next/previous navigation, so code defensively
        return INextPreviousProvider(aq_parent(aq_inner(self.context)), None)


class ViewletBase(NextPreviousView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(ViewletBase, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager

    def update(self):
        pass

    def portal_url(self):
        tool = getToolByName(self.context, 'portal_url')
        portal = tool.getPortalObject()
        return portal.absolute_url()


class NextPreviousViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('nextprevious.pt')


class NextPreviousLinksViewlet(ViewletBase):
    render = ZopeTwoPageTemplateFile('links.pt')
