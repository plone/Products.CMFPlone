
from Products.CMFPlone.browser.interfaces import IRelatedPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView

class RelatedPortlet(BrowserView):
    implements(IRelatedPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request
