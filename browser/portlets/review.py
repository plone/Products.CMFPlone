
from Products.CMFPlone.browser.interfaces import IReviewPortlet

from zope.interface import implements
from zope.component import getView
from Products.Five import BrowserView

class ReviewPortlet(BrowserView):
    implements(IReviewPortlet)

    def __init__(self, context, request):
        self.context = context
        self.request = request

