from warnings import warn

from zope.interface import implements
from zope.component import getMultiAdapter

from Acquisition import aq_inner
from OFS.SimpleItem import SimpleItem
from Products.Five import BrowserView

from plone.app.portlets.browser.interfaces import IPortletAdding

class PortletAdding(SimpleItem, BrowserView):
    implements(IPortletAdding)

    def add(self, content):
        """Add the rule to the context
        """
        context = aq_inner(self.context)
        context.saveAssignment(content)
        
    def nextURL(self):
        context = aq_parent(aq_inner(self.context))
        url = str(getMultiAdapter((context, self.request), name=u"absolute_url"))
        return url + '/@@manage-portlets'

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False