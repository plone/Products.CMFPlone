from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from OFS.Traversable import Traversable
from Acquisition import aq_base, aq_parent
from DateTime import DateTime

import sys


debug = 1  # enable/disable logging
type_map = {}

class FactoryTool(UniqueObject, SimpleItem):
    """ """
    id = 'portal_factory'
    meta_type= 'Plone Factory Tool'
    security = ClassSecurityInfo()

    def _generateTypeMap(self):
        types_tool = getattr(self.getParentNode(), 'portal_types')
        content_types = types_tool.listContentTypes()
        
        global type_map
        type_map = {}
        for t in content_types:
            type_map[t.replace(' ', '')] = t

    def __bobo_traverse__(self, REQUEST, name):
        """ """
        global type_map
        type_name = type_map.get(name, None)
        if not type_name:
            # refresh type map
            self._generateTypeMap()
            type_name = type_map.get(name, None)

        if not type_name:
            # unknown type -- ignore and do normal traversal
            return getattr(aq_parent(self), name)

        self.log('returning PendingCreate(%s)' % type_name, '__bobo_traverse__')
        return PendingCreate(type_name).__of__(aq_parent(self))  # wrap in acquisition layer


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
        prefix = 'FactoryTool'
        if loc:
            prefix = prefix + '. ' + str(loc)
        sys.stdout.write(prefix+': '+str(msg)+'\n')

InitializeClass(FactoryTool)


class PendingCreate(SimpleItem):
    """ """
    meta_type= 'Object With Creation Pending'
    security = ClassSecurityInfo()

    def __init__(self, type):
        now = DateTime()
        self.id = type.replace(' ', '_')+'.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%H%M%S')
        self._type = type
        self.Title = ''

    security.declarePublic('getPendingCreateType')
    def getPendingCreateType(self):
        """ """
        return self._type


    def invokeFactory(self, id, *args, **kw):
        self.log('invoking factory')
        container = self.getParentNode()
        container.invokeFactory(self._type, id, *args, **kw)
        return getattr(container, id)


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
        prefix = 'PendingCreate'
        if loc:
            prefix = prefix + '. ' + str(loc)
        sys.stdout.write(prefix+': '+str(msg)+'\n')

InitializeClass(PendingCreate)
