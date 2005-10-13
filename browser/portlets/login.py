from zope.component import getView
from zope.interface import implements

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import ILoginPortlet


class LoginPortlet(utils.BrowserView):
    implements(ILoginPortlet)
