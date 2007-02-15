from zope.interface import Interface
from zope.component import adapts, getMultiAdapter

from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IBrowserRequest

from Acquisition import Explicit, aq_inner, aq_parent
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import isDefaultPage

from plone.portlets.interfaces import IPortletRenderer, ILocalPortletAssignable
from plone.portlets.manager import PortletManagerRenderer as BasePortletManagerRenderer

from plone.app.portlets.interfaces import IColumn

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
    adapts(Interface, IBrowserRequest, IBrowserView, IColumn)
    template = ViewPageTemplateFile('browser/templates/column.pt')

    def _context(self):
        context = aq_inner(self.context)
        if isDefaultPage(context, self.request):
            return aq_parent(context)
        else:
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