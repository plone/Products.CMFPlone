from zope.interface import implements

from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.memoize import view, instance

from Products.Five.browser import BrowserView
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