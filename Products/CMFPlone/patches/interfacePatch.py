# Fixes to avoid interface failures, either by broken implementation
# or broken interface declaration.

# 1. Provide some methods to ObjectManager to silent warnings from
# zope.app.container.interfaces.IContainer

from Globals import InitializeClass
from AccessControl.Permissions import access_contents_information
from OFS.ObjectManager import ObjectManager
from Products.CMFPlone.utils import _getSecurity

def __delitem__(self, name):
    self.manage_delObjects(ids=[name])
ObjectManager.__delitem__ = __delitem__

def __contains__(self, name):
    return name in self.objectIds()
ObjectManager.__contains__ = __contains__

def keys(self):
    return self.objectIds()
ObjectManager.keys = keys

def items(self):
    return self.objectItems()
ObjectManager.items = items

def values(self):
    return self.objectValues()
ObjectManager.values = values

def get(self, key, default=None):
    return self._getOb(key, default)
ObjectManager.get = get

def __setitem__(self, key, value):
    return self._setObject(key, value)
ObjectManager.__setitem__ = __setitem__

def __iter__(self):
    return iter(self.objectIds())
ObjectManager.__iter__ = __iter__

# Protect new methods.
security = _getSecurity(ObjectManager)
security.declareProtected(access_contents_information,
                          'get', 'keys', 'items', 'values')
InitializeClass(ObjectManager)
