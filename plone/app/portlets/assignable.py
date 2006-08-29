from Acquisition import aq_base, Explicit
from OFS.SimpleItem import SimpleItem

from zope.interface import implements
from zope.component import adapts

from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletManager

from plone.portlets.assignable import LocalPortletAssignmentManager as BaseManager

class LocalPortletAssignmentManager(SimpleItem, BaseManager):
    """Default implementation of a portlet assignable for contexts (content 
    objects).
    """
    implements(ILocalPortletAssignmentManager)
    adapts(ILocalPortletAssignable, IPortletManager)

    def __init__(self, context, manager):
        BaseManager.__init__(self, context, manager)
        
    def __getitem__(self, key):
        return self._assignments[self._key(key)].__of__(self)

    def get(self, key, default=None):
        try:
            return self[key].__of__(self)
        except KeyError:
            return default

    def values(self):
        return [a.__of__(self) for a in self._assignments]
        
    def items(self):
        items = []
        idx = 0
        for a in self._assignments:
            items.append((idx, a.__of__(self)))
            idx += 1
        return items
    
    def saveAssignment(self, assignment):
        assignment = aq_base(assignment)
        key = getattr(assignment, '__name__', None)
        try:
            key = self._key(key)
        except KeyError:
            key = None
        if key is not None:
            self._assignments[key] = assignment
        else:
            key = len(self._assignments)
            assignment.__name__ = str(key)
            self._assignments.append(assignment)
            
        assignment.__parent__ = self