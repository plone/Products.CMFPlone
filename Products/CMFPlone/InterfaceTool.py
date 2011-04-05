from zope.dottedname.resolve import resolve
from zope.interface import implements
from zope.interface import implementedBy
from zope.interface import Interface
from zope.interface.interfaces import IMethod

from Products.CMFPlone.interfaces import IInterfaceTool
from Acquisition import aq_base
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject

from OFS.SimpleItem import SimpleItem
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

_marker = ('module_finder', )


class InterfaceTool(PloneBaseTool, UniqueObject, SimpleItem):
    """ This tool exposes the interface package for TTW applications,
    by accepting a dotted name of an interface and exporting the
    IInterface API """

    implements(IInterfaceTool)

    id = 'portal_interface'
    meta_type= 'Portal Interface Tool'
    security = ClassSecurityInfo()

    security.declarePublic('objectImplements')
    def objectImplements(self, obj, dotted_name):
        """ Asserts if an object implements a given interface """
        obj = aq_base(obj)
        iface = resolveInterface(dotted_name)
        return iface.providedBy(obj)

    security.declarePublic('classImplements')
    def classImplements(self, obj, dotted_name):
        """ Asserts if an object's class implements a given interface """
        iface = resolveInterface(dotted_name)
        return iface.providedBy(obj)

    security.declarePublic('namesAndDescriptions')
    def namesAndDescriptions(self, dotted_name, all=0):
        """ Returns a list of pairs (name, description) for a given
        interface"""
        iface = resolveInterface(dotted_name)
        nd = iface.namesAndDescriptions(all=all)
        return [(n, d.getDoc()) for n, d in nd]

    security.declarePublic('getInterfacesOf')
    def getInterfacesOf(self, object):
        """Returns the list of interfaces which are implemented by the object
        """
        return tuple(implementedBy(object).flattened())

    def getBaseInterfacesOf(self, object):
        """Returns all base interfaces of an object but no direct interfaces

        Base interfaces are the interfaces which are the super interfaces of the
        direct interfaces
        """
        ifaces = self.getInterfacesOf(object)
        bases = []
        for iface in ifaces:
            visitBaseInterfaces(iface, bases)
        return [biface for biface in bases if biface not in ifaces]

    def getInterfaceInformations(self, iface):
        """Gets all useful informations from an iface

        * name
        * dotted name
        * trimmed doc string
        * base interfaces
        * methods with signature and trimmed doc string
        * attributes with trimemd doc string
        """
        bases = [base for base in iface.getBases()]

        attributes = []
        methods = []
        for name, desc in iface.namesAndDescriptions():
            if IMethod.providedBy(desc):
                methods.append({'signature': desc.getSignatureString(),
                                'name': desc.getName(),
                                'doc': _trim_doc_string(desc.getDoc()),
                               })
            else:
                attributes.append({'name': desc.getName(),
                                   'doc': _trim_doc_string(desc.getDoc()),
                                  })

        result = {
            'name': iface.getName(),
            'dotted_name': getDottedName(iface),
            'doc': _trim_doc_string(desc.getDoc()),
            'bases': bases,
            'base_names': [getDottedName(iface) for base in bases],
            'attributes': attributes,
            'methods': methods,
            }

        return result


def resolveInterface(dotted_name):
    klass = resolve(dotted_name)
    if issubclass(klass, Interface):
        return klass
    else:
        raise ValueError, '%r is not a valid Interface.' % dotted_name


def getDottedName(iface):
    return "%s.%s" % (iface.__module__, iface.__name__)


def _trim_doc_string(text):
    """
    Trims a doc string to make it format
    correctly with structured text.
    """
    text = text.strip().replace('\r\n', '\n')
    lines = text.split('\n')
    nlines = [lines[0]]
    if len(lines) > 1:
        min_indent=None
        for line in lines[1:]:
            indent=len(line) - len(line.lstrip())
            if indent < min_indent or min_indent is None:
                min_indent=indent
        for line in lines[1:]:
            nlines.append(line[min_indent:])
    return '\n'.join(nlines)


def visitBaseInterfaces(iface, lst):
    bases = iface.getBases()
    for base in bases:
        if base in lst:
            return
        lst.append(base)
        visitBaseInterfaces(iface, lst)

InitializeClass(InterfaceTool)
registerToolInterface('portal_interface', IInterfaceTool)
