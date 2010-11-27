#
# interface testing suite
#

from Testing import ZopeTestCase

from types import TupleType, TypeType, ClassType
from zope.interface.interface import InterfaceClass
from ExtensionClass import ExtensionClass

from zope.interface import implementedBy, providedBy

###############################################################################
###               import classes and interfaces for testing                 ###
###############################################################################

from Products.CMFPlone.ActionIconsTool import ActionIconsTool
from Products.CMFPlone.ActionsTool import ActionsTool
from Products.CMFPlone.CalendarTool import CalendarTool
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.DiscussionTool import DiscussionTool
from Products.CMFPlone.FactoryTool import FactoryTool, TempFolder
from Products.CMFPlone.InterfaceTool import InterfaceTool
from Products.CMFPlone.MetadataTool import MetadataTool
from Products.CMFPlone.MigrationTool import MigrationTool
from Products.CMFPlone.PloneControlPanel import PloneControlPanel, PloneConfiglet
from Products.CMFPlone.PloneFolder import OrderedContainer, BasePloneFolder, PloneFolder
from Products.CMFPlone.PloneTool import PloneTool
from Products.CMFPlone.Portal import PloneSite
from Products.CMFPlone.PropertiesTool import PropertiesTool, SimpleItemWithProperties
from Products.CMFPlone.QuickInstallerTool import QuickInstallerTool
from Products.CMFPlone.RegistrationTool import RegistrationTool
from Products.CMFPlone.SkinsTool import SkinsTool
from Products.CMFPlone.SyndicationTool import SyndicationTool
from Products.CMFPlone.TypesTool import TypesTool
from Products.CMFPlone.UndoTool import UndoTool
from Products.CMFPlone.URLTool import URLTool
from Products.CMFPlone.WorkflowTool import WorkflowTool

def className(klass):
    """ get the short class name """
    if not isinstance(klass, (TypeType, ClassType,
                              ExtensionClass, InterfaceClass)):
        # Looks like an instance, get it's class.
        if hasattr(klass, '__class__'):
            klass = klass.__class__
    return klass.__name__

def dottedName(klass):
    return "%s.%s" % (klass.__module__, klass.__name__)

# list of tests
tests = []

class InterfaceTest(ZopeTestCase.ZopeTestCase):
    """general interface testing class

    klass - the class object to test
    forcedImpl - a list of interface class objects that the class klass
        *must* implement to fullfil this test

    This test class doesn't implement a test* method so you have to provide
    a test method in your implementation. See above for two examples. One
    example uses the special magic of setattr::

        setattr(MyClass, MyMethodName, lambda self: self._testStuff())

    """

    _setup_fixture = 0  # No default fixture

    klass = None    # test this class
    instance = None # test this instance
    forcedImpl = () # class must implement this tuple of interfaces

    def interfaceImplementedByInstanceOf(self, klass, interface):
        """ tests if the klass implements the interface in the right way """
        from zope.interface.verify import verifyClass
        from zope.interface.exceptions import BrokenImplementation, DoesNotImplement
        from zope.interface.exceptions import BrokenMethodImplementation

        # is the class really implemented by the given interface?
        self.failUnless(interface.implementedBy(klass),
            'The class %s does not implement %s' % (dottedName(klass),
                                                    dottedName(interface)))
        # verify if the implementation is correct
        try:
            verifyClass(interface, klass)
        except (BrokenImplementation, DoesNotImplement,
                BrokenMethodImplementation), errmsg:
            self.fail('The class %s does not implement %s correctly: \n%s'
                      % (dottedName(klass), dottedName(interface), errmsg))

    def interfaceImplementedBy(self, instance, interface):
        """ tests if the instance implements the interface in the right way """
        from zope.interface.verify import verifyObject
        from zope.interface.exceptions import BrokenImplementation, DoesNotImplement
        from zope.interface.exceptions import BrokenMethodImplementation

        # is the class really implemented by the given interface?
        self.failUnless(interface.providedBy(instance),
            'The instance of %s does not implement %s' % (dottedName(instance),
                                                          dottedName(interface)))
        # verify if the implementation is correct
        try:
            verifyObject(interface, instance)
        except (BrokenImplementation, DoesNotImplement,
          BrokenMethodImplementation), errmsg:
            self.fail('The instance of %s does not implement %s correctly: \n%s'
                % (dottedName(instance), dottedName(interface), errmsg))

    def getImplementsOfInstanceOf(self, klass):
        """ returns the interfaces implemented by the klass (flat)"""
        return tuple(implementedBy(klass))

    def getImplementsOf(self, instance):
        """ returns the interfaces implemented by the instance (flat)"""
        return tuple(providedBy(instance))

    def doesImplementByInstanceOf(self, klass, interfaces):
        """ make sure that the klass implements at least these interfaces"""
        if type(interfaces) is not TupleType:
            interfaces = (interfaces)
        impl = self.getImplementsOfInstanceOf(klass)
        for interface in interfaces:
            self.failUnless(
                interface in impl,
                'The class %s does not implement %s' % (dottedName(klass),
                                                        dottedName(interface)))

    def doesImplementBy(self, instance, interfaces):
        """ make sure that the klass implements at least these interfaces"""
        if type(interfaces) is not TupleType:
            interfaces = (interfaces)
        impl = self.getImplementsOf(instance)
        for interface in interfaces:
            self.failUnless(
                interface in impl,
                'The instance of %s does not implement %s' % (dottedName(instance),
                                                              dottedName(interface)))

    def _testStuff(self):
        """ test self.klass and self.instance """
        if self.klass:
            if self.forcedImpl:
                self.doesImplementByInstanceOf(self.klass, self.forcedImpl)
            for iface in self.getImplementsOfInstanceOf(self.klass):
                self.interfaceImplementedByInstanceOf(self.klass, iface)
        if self.instance:
            if self.forcedImpl:
                self.doesImplementBy(self.instance, self.forcedImpl)
            for iface in self.getImplementsOf(self.instance):
                self.interfaceImplementedBy(self.instance, iface)


class zope_interface_test(ZopeTestCase.ZopeTestCase):
    """general zope.interface testing class

    klass - the class object to test
    forcedImpl - a list of interface class objects that the class klass
        *must* implement to fullfil this test

    This test class doesn't implement a test* method so you have to provide
    a test method in your implementation. See above for two examples. One
    example uses the special magic of setattr::

        setattr(MyClass, MyMethodName, lambda self: self._testStuff())

    """

    _setup_fixture = 0  # No default fixture

    klass = None    # test this class
    instance = None # test this instance
    forcedImpl = () # class must implement this tuple of interfaces

    def interfaceImplementedBy(self, klass, interface):
        """ tests if the klass implements the interface in the right way """

        from zope.interface.verify import verifyClass
        from zope.interface.exceptions import BrokenImplementation, DoesNotImplement
        from zope.interface.exceptions import BrokenMethodImplementation

        # is the class really implemented by the given interface?
        self.failUnless(interface.implementedBy(klass),
            'The class %s does not implement %s' % (dottedName(klass),
                                                    dottedName(interface)))
        # verify if the implementation is correct
        try:
            verifyClass(interface, klass)
        except (BrokenImplementation, DoesNotImplement,
                BrokenMethodImplementation), errmsg:
            self.fail('The class %s does not implement %s correctly: \n%s'
                      % (dottedName(klass), dottedName(interface), errmsg))

    def interfaceProvidedBy(self, instance, interface):
        """ tests if the instance implements the interface in the right way """
        from zope.interface.verify import verifyObject
        from zope.interface.exceptions import BrokenImplementation, DoesNotImplement
        from zope.interface.exceptions import BrokenMethodImplementation

        # is the class really implemented by the given interface?
        self.failUnless(interface.providedBy(instance),
            'The instance of %s does not provide %s' % (dottedName(instance),
                                                        dottedName(interface)))
        # verify if the implementation is correct
        try:
            verifyObject(interface, instance)
        except (BrokenImplementation, DoesNotImplement,
                BrokenMethodImplementation), errmsg:
            self.fail('The instance of %s does not provide %s correctly: \n%s'
                      % (dottedName(instance), dottedName(interface), errmsg))

    def getImplementedBy(self, klass):
        """ returns the interfaces implemented by the klass (flat)"""
        from zope.interface import implementedBy
        return implementedBy(klass)

    def getProvidedBy(self, instance):
        """ returns the interfaces implemented by the instance (flat)"""
        from zope.interface import providedBy
        return providedBy(instance)

    def doesImplementedBy(self, klass, interfaces):
        """ make sure that the klass implements at least these interfaces"""
        impl = self.getImplementedBy(klass)
        for interface in interfaces:
            self.failUnless(
                interface in impl,
                'The class %s does not implement %s' % (dottedName(klass),
                                                        dottedName(interface)))

    def doesProvidedBy(self, instance, interfaces):
        """ make sure that the klass implements at least these interfaces"""
        impl = self.getProvidedBy(instance)
        for interface in interfaces:
            self.failUnless(
                interface in impl,
                'The instance of %s does not provide %s' % (dottedName(instance),
                                                            dottedName(interface)))

    def _testStuff(self):
        """ test self.klass and self.instance """
        if self.klass:
            if self.forcedImpl:
                self.doesImplementedBy(self.klass, self.forcedImpl)
            for iface in self.getImplementedBy(self.klass):
                self.interfaceImplementedBy(self.klass, iface)
        if self.instance:
            if self.forcedImpl:
                self.doesProvidedBy(self.instance, self.forcedImpl)
            for iface in self.getProvidedBy(self.instance):
                self.interfaceProvidedBy(self.instance, iface)


###############################################################################
###                         testing starts here                             ###
###############################################################################

# format: (class object, (list interface objects))
testClasses = [
    (ActionIconsTool, ()),
    (ActionsTool, ()),
    (CalendarTool, ()),
    (CatalogTool, ()),
    (DiscussionTool, ()),
    (FactoryTool, ()), (TempFolder, ()),
    (InterfaceTool, ()),
    (MetadataTool, ()),
    (MigrationTool, ()),
    (PloneControlPanel, ()), (PloneConfiglet, ()),
    (OrderedContainer, ()), (BasePloneFolder, ()), (PloneFolder, ()),
    (PloneTool, ()),
    (PloneSite, ()),
    (PropertiesTool, ()), (SimpleItemWithProperties, ()),
    (QuickInstallerTool, ()),
    (RegistrationTool, ()),
    (SkinsTool, ()),
    (SyndicationTool, ()),
    (TypesTool, ()),
    (UndoTool, ()),
    (URLTool, ()),
    (WorkflowTool, ()),
]

for testClass in testClasses:
    klass, forcedImpl = testClass
    name = className(klass)
    funcName = 'test%sInterface' % name

    class KlassInterfaceTest(InterfaceTest):
        """ implementation for %s """ % name
        klass      = klass
        forcedImpl = forcedImpl

    # add the testing method to the class to get a nice name
    setattr(KlassInterfaceTest, funcName, lambda self: self._testStuff())
    tests.append(KlassInterfaceTest)

    class KlassInterfaceTest(zope_interface_test):
        """ implementation for %s """ % name
        klass      = klass
        forcedImpl = forcedImpl

    # add the testing method to the class to get a nice name
    setattr(KlassInterfaceTest, funcName, lambda self: self._testStuff())
    tests.append(KlassInterfaceTest)

import unittest

def test_suite():
    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(unittest.makeSuite(test))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
