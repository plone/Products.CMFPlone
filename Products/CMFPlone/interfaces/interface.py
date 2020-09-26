from Products.CMFPlone.interfaces.basetool import IPloneBaseTool
from zope.interface import Attribute


class IInterfaceTool(IPloneBaseTool):
    """ This tool exposes the interface package for TTW applications,
    by accepting a dotted name of an interface and exporting the
    IInterface API """

    id = Attribute('id', 'Must be set to "portal_interface"')

    def objectImplements(obj, dotted_name):
        """ Asserts if an object implements a given interface """

    def classImplements(obj, dotted_name):
        """ Asserts if an object's class implements a given interface """

    def namesAndDescriptions(dotted_name, all=0):
        """ Returns a list of pairs (name, description) for a given
        interface"""
