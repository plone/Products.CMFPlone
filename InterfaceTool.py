import sys
from types import ClassType, ModuleType
from zLOG import LOG, INFO, WARNING
from Products.CMFPlone.interfaces.interface import Interface, Attribute
from Products.CMFPlone.interfaces.InterfaceTool import IInterfaceTool
from Acquisition import aq_inner, aq_parent, aq_base
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.utils import _checkPermission, \
     _getAuthenticatedUser, limitGrantedRoles
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

def log(summary='', text='', log_level=INFO):
    LOG('InterfaceTool', log_level, summary, text)

_marker = ('module_finder',)

class InterfaceTool(PloneBaseTool, UniqueObject, SimpleItem):
    """ This tool exposes the interface package for TTW applications,
    by accepting a dotted name of an interface and exporting the
    IInterface API """
  
    __implements__ = (PloneBaseTool.__implements__, IInterfaceTool, 
                      SimpleItem.__implements__, )

    id = 'portal_interface'
    meta_type= 'Portal Interface Tool'
    security = ClassSecurityInfo()

    security.declarePublic('objectImplements')
    def objectImplements(self, obj, dotted_name):
        """ Asserts if an object implements a given interface """
        obj = aq_base(obj)
        iface = resolveInterface(dotted_name)
        return iface.isImplementedBy(obj)

    security.declarePublic('classImplements')
    def classImplements(self, obj, dotted_name):
        """ Asserts if an object's class implements a given interface """
        klass = aq_base(obj).__class__
        iface = resolveInterface(dotted_name)
        return iface.isImplementedBy(klass)

    security.declarePublic('namesAndDescriptions')
    def namesAndDescriptions(self, dotted_name, all=0):
        """ Returns a list of pairs (name, description) for a given
        interface"""
        iface = resolveInterface(dotted_name)
        nd = iface.namesAndDescriptions(all=all)
        return [(n, d.getDoc()) for n, d in nd]

def resolveInterface(dotted_name):
    parts = dotted_name.split('.')
    m_name = '.'.join(parts[:-1])
    k_name = parts[-1]
    module = __import__(m_name, globals(), locals(), [k_name])
    klass = getattr(module, k_name)
    if not issubclass(klass, Interface):
        raise ValueError, '%r is not a valid Interface.' % dotted_name
    return klass

def getDottedName(iface):
    return "%s.%s" % (iface.__module__, iface.__name__)

class InterfaceFinder:

    _visited = {}
    _found = {}

    def findInterfaces(self, n=None, module=_marker):
        # return class reference info
        dict={}
        pairs = []
        if module is _marker:
            import Products
            module = Products
        self._visited[module] = None
        for sym in dir(module):
            ob=getattr(module, sym)
            if type(ob) is type(Interface) and \
               issubclass(ob, Interface) and \
               ob is not Interface:
                self.found(ob)
            elif type(ob) is ModuleType and ob not in self._visited.keys():
                self.findInterfaces(module=ob)

        ifaces = self._found.keys()
        ifaces.sort()
        ifaces.reverse()
        if n is not None:
            ifaces = ifaces[:n]
        return ifaces

    def found(self, iface):
        self._found[getDottedName(iface)] = iface

InitializeClass(InterfaceTool)
