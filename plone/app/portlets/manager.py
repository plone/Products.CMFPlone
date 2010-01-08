import logging
import sys

from plone.portlets.interfaces import IPortletRenderer, ILocalPortletAssignable
from plone.portlets.manager import PortletManagerRenderer as BasePortletManagerRenderer
from plone.app.layout.navigation.defaultpage import isDefaultPage
from zope.component import adapts, getMultiAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Acquisition import Explicit, aq_inner, aq_parent, aq_acquire
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError

from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.interfaces import IDashboard

logger = logging.getLogger('portlets')

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

class ColumnPortletManagerRenderer(PortletManagerRenderer):
    """A renderer for the column portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IColumn)
    template = ViewPageTemplateFile('browser/templates/column.pt')
    error_message = ViewPageTemplateFile('browser/templates/error_message.pt')

    def _context(self):
        context = aq_inner(self.context)
        container = aq_parent(context)
        if isDefaultPage(container, context):
            return container
        return context

    def base_url(self):
        """If context is a default-page, return URL of folder, else
        return URL of context.
        """
        return str(getMultiAdapter((self._context(), self.request,), name=u'absolute_url'))

    def can_manage_portlets(self):
        context = self._context()
        if not ILocalPortletAssignable.providedBy(context):
            return False
        mtool = getToolByName(context, 'portal_membership')
        return mtool.checkPermission("Portlets: Manage portlets", context)

    def safe_render(self, portlet_renderer):
        try:
            return portlet_renderer.render()
        except ConflictError:
            raise
        except Exception:
            logger.exception('Error while rendering %r' % (self,))
            aq_acquire(self, 'error_log').raising(sys.exc_info())
            return self.error_message()

class DashboardPortletManagerRenderer(ColumnPortletManagerRenderer):
    """Render a column of the dashboard
    """

    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IDashboard)
    template = ViewPageTemplateFile('browser/templates/dashboard-column.pt')