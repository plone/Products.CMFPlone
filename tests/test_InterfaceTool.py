import Zope

try:
    Zope.startup()
except AttributeError: # Zope > 2.6
    pass

from unittest import TestCase, TestSuite, makeSuite, main
from Products.CMFPlone.InterfaceTool import resolveInterface, getDottedName, \
     InterfaceTool, InterfaceFinder
from Products.CMFCore.interfaces.DublinCore import DublinCore
from Products.CMFCore.interfaces.Contentish import Contentish
from Products.CMFCore.interfaces.Dynamic import DynamicType
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.Document import Document
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

class MyPortalContent(Contentish):
    pass

class A(PortalContent, DefaultDublinCoreImpl):
    __implements__ = PortalContent.__implements__, \
                     DefaultDublinCoreImpl.__implements__
    pass

class B(PortalContent, DefaultDublinCoreImpl):
    __implements__ = MyPortalContent, DefaultDublinCoreImpl.__implements__

class InterfaceResolutionTests(TestCase):

    def test_dublincore(self):
        dotted_name = getDottedName(DublinCore)
        self.assertEquals(resolveInterface(dotted_name), DublinCore)

    def test_contentish(self):
        dotted_name = getDottedName(Contentish)
        self.assertEquals(resolveInterface(dotted_name), Contentish)

    def test_non_interface(self):
        dotted_name = getDottedName(PortalContent)
        self.assertRaises(ValueError, resolveInterface, dotted_name)

class InterfaceToolTests(TestCase):

    def test_objectImplements(self):
        itool = InterfaceTool()
        content = PortalContent()
        document = Document(id='bla')
        dc = DefaultDublinCoreImpl()
        a = A()
        b = B()
        objImplements = itool.objectImplements
        self.failUnless(objImplements(content, getDottedName(Contentish)))
        self.failUnless(objImplements(document, getDottedName(Contentish)))
        self.failUnless(objImplements(document, getDottedName(DublinCore)))
        self.failUnless(objImplements(dc, getDottedName(DublinCore)))
        self.failUnless(objImplements(a, getDottedName(Contentish)))
        self.failUnless(objImplements(a, getDottedName(DublinCore)))
        self.failIf(objImplements(a, getDottedName(MyPortalContent)))
        self.failUnless(objImplements(b, getDottedName(MyPortalContent)))
        self.failUnless(objImplements(b, getDottedName(Contentish)))
        self.failUnless(objImplements(b, getDottedName(DublinCore)))

    def test_availableIfaces(self):
        from Products.CMFPlone.interfaces import InterfaceTool
        ifaces = InterfaceFinder().findInterfaces(module=InterfaceTool)
        self.assertEquals(ifaces,
                          [getDottedName(InterfaceTool.IInterfaceTool)])

    def test_namesAndDescriptions(self):
        from Products.CMFPlone.interfaces.InterfaceTool import IInterfaceTool
        itool = InterfaceTool()
        nd = itool.namesAndDescriptions(getDottedName(IInterfaceTool))
        nd2 = IInterfaceTool.namesAndDescriptions()
        nd2 = [(n, d.getDoc()) for n, d in nd2]
        self.assertEquals(nd, nd2)

def test_suite():
    return TestSuite((
        makeSuite(InterfaceToolTests),
        makeSuite(InterfaceResolutionTests),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
