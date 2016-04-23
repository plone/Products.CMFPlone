# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.component import getMultiAdapter


class NextPreviousView(BrowserView):
    """Information about next/previous navigation
    """

    def next(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getNextItem(aq_inner(self.context))

    def previous(self):
        provider = self._provider()
        if provider is None:
            return None
        return provider.getPreviousItem(aq_inner(self.context))

    def enabled(self):
        provider = self._provider()
        if provider is None:
            return False
        return provider.enabled

    def _provider(self):
        # Note - the next/previous provider is the container of this object!
        # This may not support next/previous navigation, so code defensively
        return INextPreviousProvider(aq_parent(aq_inner(self.context)), None)

    def isViewTemplate(self):
        plone = getMultiAdapter((
            self.context, self.request), name=u'plone_context_state')
        return plone.is_view_template()


class NextPreviousViewlet(ViewletBase, NextPreviousView):
    index = ZopeTwoPageTemplateFile('nextprevious.pt')


class NextPreviousLinksViewlet(ViewletBase, NextPreviousView):
    index = ZopeTwoPageTemplateFile('links.pt')
