# -*- coding: utf-8 -*-
from Acquisition import aq_base
from interfaces import IInterfaceInformation
from plone.memoize.view import memoize
from Products.Five.browser import BrowserView
from zope.dottedname.resolve import resolve
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import providedBy
from zope.interface.interfaces import IMethod


def resolveInterface(dotted_name):
    klass = resolve(dotted_name)
    if not issubclass(klass, Interface):
        raise ValueError('%r is not a valid Interface.' % dotted_name)
    return klass


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
        min_indent = None
        for line in lines[1:]:
            indent = len(line) - len(line.lstrip())
            if indent < min_indent or min_indent is None:
                min_indent = indent
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


@implementer(IInterfaceInformation)
class InterfaceInformation(BrowserView):

    @memoize
    def provides(self, dotted_name):
        iface = resolveInterface(dotted_name)
        return iface.providedBy(aq_base(self.context))

    @memoize
    def class_provides(self, dotted_name):
        iface = resolveInterface(dotted_name)
        return iface.providedBy(aq_base(self.context).__class__)

    @memoize
    def names_and_descriptions(self, dotted_name, all=0):
        """ Returns a list of pairs (name, description) for a given
        interface"""
        iface = resolveInterface(dotted_name)
        nd = iface.namesAndDescriptions(all=all)
        return [(n, d.getDoc()) for n, d in nd]

    @memoize
    def get_interfaces(self):
        """Returns the list of interfaces which are implemented by the object
        """
        return tuple(providedBy(aq_base(self.context)).flattened())

    def get_base_interface(self):
        """Returns all base interfaces of an object but no direct interfaces

        Base interfaces are the interfaces which are the super interfaces of
        the direct interfaces
        """
        ifaces = self.get_interfaces()
        bases = []
        for iface in ifaces:
            visitBaseInterfaces(iface, bases)
        return [biface for biface in bases if biface not in ifaces]

    def get_interface_informations(self, iface):
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
                                'doc': _trim_doc_string(desc.getDoc())
                                }
                               )
            else:
                attributes.append({'name': desc.getName(),
                                   'doc': _trim_doc_string(desc.getDoc()),
                                   }
                                  )

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
