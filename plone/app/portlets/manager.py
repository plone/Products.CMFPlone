from zope.component import getMultiAdapter

from Acquisition import Explicit

from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.manager import PortletManagerRenderer as BasePortletManagerRenderer

class PortletManagerRenderer(BasePortletManagerRenderer, Explicit):
    """A Zope 2 implementation of the default PortletManagerRenderer
    """

    def _dataToPortlet(self, data):
        """Helper method to get the correct IPortletRenderer for the given
        data object.
        """
        portlet = getMultiAdapter((self.context, self.request, self.__parent__,
                                        self.manager, data,), IPortletRenderer)
        return portlet.__of__(self.context)