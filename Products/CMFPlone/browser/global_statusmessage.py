from zope.interface import implements

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone.browser.interfaces import IGlobalStatusMessage


class GlobalStatusMessage(BrowserView):
    """Display messages to the current user"""
    implements(IGlobalStatusMessage)

    index = ViewPageTemplateFile('templates/global_statusmessage.pt')

    def __call__(self):
        return self.index()

    @property
    def macros(self):
        return self.index.macros
