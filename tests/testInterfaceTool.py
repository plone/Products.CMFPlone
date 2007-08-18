#
# InterfaceTool tests
#

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.interfaces.DublinCore import DublinCore
from Products.CMFCore.interfaces.Contentish import Contentish
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFDefault.Document import Document

from Products.CMFPlone.InterfaceTool import resolveInterface, getDottedName
from Products.CMFPlone.utils import classImplements


class MyPortalContent(Contentish): pass

class A(PortalContent, DefaultDublinCoreImpl):
    __implements__ = PortalContent.__implements__, \
                     DefaultDublinCoreImpl.__implements__
classImplements(A, A.__implements__)

class B(PortalContent, DefaultDublinCoreImpl):
    __implements__ = MyPortalContent, \
                     DefaultDublinCoreImpl.__implements__
classImplements(B, B.__implements__)


class TestInterfaceResolution(ZopeTestCase.ZopeTestCase):

    def testResolveDublinCore(self):
        # DublinCore should be resolved
        dotted_name = getDottedName(DublinCore)
        self.assertEqual(resolveInterface(dotted_name), DublinCore)

    def testResolveContentish(self):
        # Contentish should be resolved
        dotted_name = getDottedName(Contentish)
        self.assertEqual(resolveInterface(dotted_name), Contentish)

    def testResolveNonInterface(self):
        # Should raise ValueError when called with non-Interface
        dotted_name = getDottedName(PortalContent)
        self.assertRaises(ValueError, resolveInterface, dotted_name)


class TestInterfaceTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.interface = self.portal.portal_interface

    def testContentImplements(self):
        content = PortalContent()
        self.failUnless(self.interface.objectImplements(content, getDottedName(Contentish)))

    def testDocumentImplements(self):
        document = Document(id='foo')
        self.failUnless(self.interface.objectImplements(document, getDottedName(Contentish)))
        self.failUnless(self.interface.objectImplements(document, getDottedName(DublinCore)))

    def testDCImplements(self):
        dc = DefaultDublinCoreImpl()
        self.failUnless(self.interface.objectImplements(dc, getDottedName(DublinCore)))

    def testAImplements(self):
        a = A()
        self.failUnless(self.interface.objectImplements(a, getDottedName(Contentish)))
        self.failUnless(self.interface.objectImplements(a, getDottedName(DublinCore)))
        self.failIf(self.interface.objectImplements(a, getDottedName(MyPortalContent)))

    def testBImplements(self):
        b = B()
        self.failUnless(self.interface.objectImplements(b, getDottedName(Contentish)))
        self.failUnless(self.interface.objectImplements(b, getDottedName(DublinCore)))
        self.failUnless(self.interface.objectImplements(b, getDottedName(MyPortalContent)))


def test_suite():
    # Normalize dotted names
    from Products.CMFPlone.tests.testInterfaceTool import TestInterfaceResolution
    from Products.CMFPlone.tests.testInterfaceTool import TestInterfaceTool

    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInterfaceResolution))
    suite.addTest(makeSuite(TestInterfaceTool))
    return suite
