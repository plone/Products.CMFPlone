from zope.interface import implements
from zope.component import adapts

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.app.container.traversal import ItemTraverser

from Acquisition import aq_base, aq_inner
from AccessControl import Unauthorized
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.utils import getToolByName

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.storage import PortletAssignmentMapping as BaseMapping

from zope.app.container.ordered import OrderedContainer
from zope.app.container.contained import setitem, uncontained

from plone.app.portlets.interfaces import IUserPortletAssignmentMapping

class PortletAssignmentMapping(BaseMapping, SimpleItem):
    """A Zope 2 version of the default assignment mapping storage.
    """
        
    def __setitem__(self, key, assignment):
        BaseMapping.__setitem__(self, key, aq_base(assignment))

class UserPortletAssignmentMapping(PortletAssignmentMapping):
    """An assignment mapping for user/dashboard portlets
    """

    implements(IUserPortletAssignmentMapping)
        
class PortletAssignmentMappingTraverser(ItemTraverser):
    """A traverser for portlet assignment mappings, that is acqusition-aware
    """
    implements(IBrowserPublisher)
    adapts(IPortletAssignmentMapping, IBrowserRequest)
    
    def publishTraverse(self, request, name):
        ob = ItemTraverser.publishTraverse(self, request, name)
        return ob.__of__(self.context)
        