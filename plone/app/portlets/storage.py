from Acquisition import aq_base

from OFS.SimpleItem import SimpleItem

from persistent.list import PersistentList
from plone.portlets.storage import PortletAssignmentMapping as BaseMapping

class PortletAssignmentMapping(BaseMapping, SimpleItem):
    """A Zope 2 version of the default assignment mapping storage.
    """

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
        BaseMapping.saveAssignment(self, assignment)