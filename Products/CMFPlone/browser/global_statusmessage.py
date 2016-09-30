# -*- coding: utf-8 -*-
from zope.interface import implementer

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone.browser.interfaces import IGlobalStatusMessage


@implementer(IGlobalStatusMessage)
class GlobalStatusMessage(BrowserView):
    """Display messages to the current user"""

    index = ViewPageTemplateFile('templates/global_statusmessage.pt')

    def __call__(self):
        return self.index()

    @property
    def macros(self):
        return self.index.macros
