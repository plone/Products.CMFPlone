from warnings import warn

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from zope.component.interfaces import IFactory
from zope.publisher.interfaces import IPublishTraverse

from zope.app.container.interfaces import INameChooser
from zope.app.container.interfaces import IContainerNamesContainer
from zope.app.container.constraints import checkFactory, checkObject

from Acquisition import Implicit

from Products.Five import BrowserView

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignable
from plone.portlets.interfaces import IPortletContext
from plone.app.portlets.interfaces import IPortletAdding

class PortletAdding(Implicit, BrowserView):
    implements(IPortletAdding)

    def add(self, content):
        """Add the object to the appropriate portlet manager
        """
        container = getUtility(IPortletManager, name=self.context.manager)
        
        context = self.context.context
        
        ctx = IPortletContext(context)
        assignable = getMultiAdapter((ctx, container), IPortletAssignable)
        assignments = assignable.getPortletAssignments()
        assignments.append(content)
        assignable.setPortletAssignments(assignments)
        
        return content
        
    def nextURL(self):
        return str(getMultiAdapter((self.context.context, self.request), name=u"absolute_url"))

    def renderAddButton(self):
        warn("The renderAddButton method is deprecated, use nameAllowed",
            DeprecationWarning, 2)

    def namesAccepted(self):
        return False

    def nameAllowed(self):
        return False
