#
# InterfaceTool tests
#

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from zope.interface import implements

from Products.CMFCore.interfaces import IDublinCore
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFDefault.Document import Document

from Products.CMFPlone.InterfaceTool import resolveInterface, getDottedName


class IMyPortalContent(IContentish):
    pass

class A(PortalContent, DefaultDublinCoreImpl):
    pass

class B(PortalContent, DefaultDublinCoreImpl):
    implements(IMyPortalContent)

class TestInterfaceResolution(ZopeTestCase.ZopeTestCase):

    def testResolveDublinCore(self):
        # DublinCore should be resolved
        dotted_name = getDottedName(IDublinCore)
        self.assertEqual(resolveInterface(dotted_name), IDublinCore)

    def testResolveContentish(self):
        # Contentish should be resolved
        dotted_name = getDottedName(IContentish)
        self.assertEqual(resolveInterface(dotted_name), IContentish)

    def testResolveNonInterface(self):
        # Should raise ValueError when called with non-Interface
        dotted_name = getDottedName(PortalContent)
        self.assertRaises(ValueError, resolveInterface, dotted_name)


class TestInterfaceTool(PloneTestCase.PloneContentLessTestCase):

    def afterSetUp(self):
        self.interface = self.portal.portal_interface

    def testContentImplements(self):
        content = PortalContent()
        self.failUnless(self.interface.objectImplements(content, getDottedName(IContentish)))

    def testDocumentImplements(self):
        document = Document(id='foo')
        self.failUnless(self.interface.objectImplements(document, getDottedName(IContentish)))
        self.failUnless(self.interface.objectImplements(document, getDottedName(IDublinCore)))

    def testDCImplements(self):
        dc = DefaultDublinCoreImpl()
        self.failUnless(self.interface.objectImplements(dc, getDottedName(IDublinCore)))

    def testAImplements(self):
        a = A()
        self.failUnless(self.interface.objectImplements(a, getDottedName(IContentish)))
        self.failUnless(self.interface.objectImplements(a, getDottedName(IDublinCore)))
        self.failIf(self.interface.objectImplements(a, getDottedName(IMyPortalContent)))

    def testBImplements(self):
        b = B()
        self.failUnless(self.interface.objectImplements(b, getDottedName(IContentish)))
        self.failUnless(self.interface.objectImplements(b, getDottedName(IDublinCore)))
        self.failUnless(self.interface.objectImplements(b, getDottedName(IMyPortalContent)))


def test_suite():
    # Normalize dotted names
    from Products.CMFPlone.tests.testInterfaceTool import TestInterfaceResolution
    from Products.CMFPlone.tests.testInterfaceTool import TestInterfaceTool

    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInterfaceResolution))
    suite.addTest(makeSuite(TestInterfaceTool))
    return suite
