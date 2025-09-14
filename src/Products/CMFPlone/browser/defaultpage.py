from Acquisition import aq_inner
from plone.base.defaultpage import get_default_page
from plone.base.defaultpage import is_default_page
from plone.base.interfaces.defaultpage import IDefaultPage
from Products.Five.browser import BrowserView
from zope.interface import implementer


@implementer(IDefaultPage)
class DefaultPage(BrowserView):
    def isDefaultPage(self, obj):
        return is_default_page(aq_inner(self.context), obj)

    def getDefaultPage(self):
        return get_default_page(aq_inner(self.context))
