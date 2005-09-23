
from Products.CMFPlone.browser.interfaces import IPrefsPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView

class PrefsPortlet(BrowserView):
    implements(IPrefsPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request

