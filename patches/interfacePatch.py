# Fixes to avoid interface failures, either by broken implementation
# or broken interface declaration.

# 1. Make WorkflowTool all_meta_types take and ignore an extra
# ``interfaces`` argument to comply with the definition of
# all_meta_types in Five.

from Products.CMFCore.WorkflowTool import WorkflowTool

orig_all_meta_types = WorkflowTool.all_meta_types
def all_meta_types(self, interfaces=None):
    return orig_all_meta_types
WorkflowTool.all_meta_types = all_meta_types

# 2. Same as above, but now for TypesTool.

from Products.CMFCore.TypesTool import TypesTool

orig_all_meta_types = TypesTool.all_meta_types
def all_meta_types(self, interfaces=None):
    return orig_all_meta_types
TypesTool.all_meta_types = all_meta_types

# 3. Provide some methods to ObjectManager to silent warnings from
# zope.app.container.interfaces.IContainer

from Globals import InitializeClass
from AccessControl.Permissions import access_contents_information
from OFS.ObjectManager import ObjectManager
from Products.Archetypes.utils import _getSecurity

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
