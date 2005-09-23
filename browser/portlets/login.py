
from Products.CMFPlone.browser.interfaces import ILoginPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView

class LoginPortlet(BrowserView):
    implements(ILoginPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request
