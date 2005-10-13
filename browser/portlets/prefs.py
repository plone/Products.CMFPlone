from zope.component import getView
from zope.interface import implements

from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import IPrefsPortlet


class PrefsPortlet(BrowserView):
    implements(IPrefsPortlet)
