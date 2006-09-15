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

class PortletAssignmentMapping(BaseMapping, SimpleItem):
    """A Zope 2 version of the default assignment mapping storage.
    """
        
    def __setitem__(self, key, assignment):
        BaseMapping.__setitem__(self, key, aq_base(assignment))
        
class PortletAssignmentMappingTraverser(ItemTraverser):
    """A traverser for portlet assignment mappings, that is acqusition-aware
    """
    implements(IBrowserPublisher)
    adapts(IPortletAssignmentMapping, IBrowserRequest)
    
    def publishTraverse(self, request, name):
        ob = ItemTraverser.publishTraverse(self, request, name)
        return ob.__of__(self.context)

class CurrentUserAssignmentMapping(SimpleItem):
    """An on-the-fly assignment mapping that knows about the current user.
    
    This is necessary because during traversal to the ++dashboard++ namespace,
    authentication hasn't kicked in yet, so we must defer to later.
    """
    implements(IPortletAssignmentMapping)
    
    def __init__(self, context, categoryMapping):
        self.context = context
        self.categoryMapping = categoryMapping
        
    def keys(self):
        return self._getUserAssignments().keys()

    def __iter__(self):
        return iter(self._getUserAssignments())

    def __getitem__(self, key):
        return self._getUserAssignments()[key]

    def get(self, key, default=None):
        return self._getUserAssignments().get(key, default)

    def values(self):
        return self._getUserAssignments().values()

    def __len__(self):
        return len(self._getUserAssignments())

    def items(self):
        return self._getUserAssignments().items()

    def __contains__(self, key):
        return self._getUserAssignments().has_key(key)

    has_key = __contains__

    def __setitem__(self, key, object):
        setitem(self, self._getUserAssignments(True).__setitem__, key, object)

    def __delitem__(self, key):
        uncontained(self._getUserAssignments()[key], self, key)
        del self._getUserAssignments()[key]
        
    def updateOrder(self, order):
        self._getUserAssignments(True).updateOrder(order)
        
    def _getUserAssignments(self, create=False):
        userId = self._getUserId()
        if userId is None and not create:
            return {}
        elif userId is None:
            raise Unauthorized, "Cannot assign portlets to anonymous via ++dashboard++"
        category = aq_inner(self.categoryMapping)
        assignments = category.get(userId, None)
        if assignments is None and not create:
            assignments = {}
        elif assignments is None:
            assignments = category[userId] = PortletAssignmentMapping()
        return assignments
        
    def _getUserId(self):
        membership = getToolByName(aq_inner(self.context), 'portal_membership', None)
        if membership.isAnonymousUser():
            return None
        
        member = membership.getAuthenticatedMember()
        
        try:
            memberId = member.getUserId()
        except AttributeError:
            try:
                memberId = member.getUserName()
            except AttributeError:
                memberId = member.getId()

        if not memberId:
            raise AttributeError, "Cannot find user id"
        
        return memberId
        