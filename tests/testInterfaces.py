#
# interface testing suite
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase 

# import Interface for interface testing
try:
    import Interface
except ImportError:
    # set dummy functions and exceptions for older zope versions
    def verifyClass(iface, candidate, tentative=0):
        return True
    def verifyObject(iface, candidate, tentative=0):
        return True
    def getImplementsOfInstances(object):
        return ()
    def flattenInterfaces(interfaces, remove_duplicates=1):
        return ()
    class BrokenImplementation(Execption): pass
    class DoesNotImplement(Execption): pass
    class BrokenMethodImplementation(Execption): pass
else:
    from Interface.Implements import getImplementsOfInstances, flattenInterfaces
    from Interface.Verify import verifyClass, verifyObject
    from Interface.Exceptions import BrokenImplementation, DoesNotImplement
    from Interface.Exceptions import BrokenMethodImplementation   

from types import TupleType

###############################################################################
###               import classes and interfaces for testing                 ###
###############################################################################

from Products.CMFPlone.ActionIconsTool import ActionIconsTool
from Products.CMFPlone.ActionsTool import ActionsTool
from Products.CMFPlone.CalendarTool import CalendarTool
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFPlone.DiscussionTool import DiscussionTool
from Products.CMFPlone.FactoryTool import FactoryTool, TempFolder
from Products.CMFPlone.FormTool import FormTool, FormValidator, CMFForm
from Products.CMFPlone.GroupDataTool import GroupDataTool
from Products.CMFPlone.GroupsTool import GroupsTool
from Products.CMFPlone.InterfaceTool import InterfaceTool
from Products.CMFPlone.LargePloneFolder import LargePloneFolder
from Products.CMFPlone.MemberDataTool import MemberDataTool, MemberData
from Products.CMFPlone.MembershipTool import MembershipTool
from Products.CMFPlone.MetadataTool import MetadataTool
from Products.CMFPlone.MigrationTool import MigrationTool
from Products.CMFPlone.NavigationTool import NavigationTool, Redirector
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.PloneContent import PloneContent
from Products.CMFPlone.PloneControlPanel import PloneControlPanel, PloneConfiglet
from Products.CMFPlone.PloneFolder import OrderedContainer, PloneFolder
from Products.CMFPlone.PloneTool import PloneTool
from Products.CMFPlone.Portal import PloneSite, PloneGenerator
from Products.CMFPlone.PrivateSitePolicy import PrivateSitePolicy
from Products.CMFPlone.PropertiesTool import PropertiesTool, SimpleItemWithProperties
from Products.CMFPlone.QuickInstallerTool import QuickInstallerTool
from Products.CMFPlone.RegistrationTool import RegistrationTool
from Products.CMFPlone.SkinsTool import SkinsTool
from Products.CMFPlone.StatelessTree import NavigationTreeViewBuilder
from Products.CMFPlone.SyndicationTool import SyndicationTool
from Products.CMFPlone.TypesTool import TypesTool
from Products.CMFPlone.UndoTool import UndoTool
from Products.CMFPlone.URLTool import URLTool
from Products.CMFPlone.WorkflowTool import WorkflowTool

def className(klass):
    """ get the short class name """
    return str(klass).split('.')[-1].split(' ')[0]

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

    klass = None    # test this class
    forcedImpl = () # class must implement this tuple of interfaces

    def _testInterfaceImplementation(self, klass, interface):
        """ tests if the klass implements the interface in the right way """
        # is the class really implemented by the given interface?
        self.failUnless(interface.isImplementedByInstancesOf(klass),
            '%s does not implement %s' % (className(klass), className(interface)))
        # verify if the implementation is correct
        try:
            verifyClass(interface, klass)
        except (BrokenImplementation, DoesNotImplement, 
          BrokenMethodImplementation), errmsg:
            self.fail('%s does not implement %s correctly: \n%s'
                % (className(klass), className(interface), errmsg)) 

    def _getImplements(self, klass):
        """ returns the interfaces implemented by the klass (flat)"""
        impl = getImplementsOfInstances(klass)
        if type(impl) is not TupleType:
             impl = (impl,)
        if impl:
            return flattenInterfaces(impl)
        
    def _doesImplement(self, klass, interfaces):
        """ make shure that the klass implements at least these interfaces"""
        if type(interfaces) is not TupleType:
            interfaces = (interfaces)
        impl = self._getImplements(klass)
        for iface in interfaces:
            self.failUnless(iface in impl, '%s does not implement %s' % (className(klass), className(iface)))

    def _testStuff(self):
        """ test self.klass """
        if self.forcedImpl:
           self._doesImplement(self.klass, self.forcedImpl)
        for iface in self._getImplements(self.klass):
           self._testInterfaceImplementation(self.klass, iface)

###############################################################################
###                         testing starts here                             ###
###############################################################################

# format: (class object, (list interface objects))
testClasses = [
    (ActionIconsTool, ()),
    (ActionsTool, ()),
    (CalendarTool, ()),
    (CatalogTool, ()),
    (DefaultCustomizationPolicy, ()),
    (DiscussionTool, ()),
    (FactoryTool, ()), (TempFolder, ()),
    (FormTool, ()), (FormValidator, ()), (CMFForm, ()),
    (GroupDataTool, ()),
    (GroupsTool, ()),
    (InterfaceTool, ()),
    (LargePloneFolder, ()),
    (MemberDataTool, ()), (MemberData, ()),
    (MembershipTool, ()), 
    (MetadataTool, ()),
    (MigrationTool, ()),
    (NavigationTool, ()), (Redirector, ()),
    # (Batch, ()), # has no __implements__
    (PloneContent, ()),
    (PloneControlPanel, ()), (PloneConfiglet, ()),
    (OrderedContainer, ()), (PloneFolder, ()),
    (PloneTool, ()),
    (PloneSite, ()), # (PloneGenerator, ()), # PloneGenerator has no __implements__
    (PrivateSitePolicy, ()),
    (PropertiesTool, ()), (SimpleItemWithProperties, ()),
    (QuickInstallerTool, ()),
    (RegistrationTool, ()),
    (SkinsTool, ()),
    (NavigationTreeViewBuilder, ()),
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


if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        for test in tests:
            suite.addTest(unittest.makeSuite(test))
        return suite