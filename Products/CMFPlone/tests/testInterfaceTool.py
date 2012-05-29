import unittest

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


class TestInterfaceResolution(unittest.TestCase):

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


class TestInterfaceTool(unittest.TestCase):

    def _makeOne(self):
        from Products.CMFPlone.InterfaceTool import InterfaceTool
        return InterfaceTool()

    def testContentImplements(self):
        tool = self._makeOne()
        content = PortalContent()
        self.assertTrue(tool.objectImplements(content,
                                              getDottedName(IContentish)))

    def testDocumentImplements(self):
        tool = self._makeOne()
        document = Document(id='foo')
        self.assertTrue(tool.objectImplements(document,
                        getDottedName(IContentish)))
        self.assertTrue(tool.objectImplements(document,
                        getDottedName(IDublinCore)))

    def testDCImplements(self):
        tool = self._makeOne()
        dc = DefaultDublinCoreImpl()
        self.assertTrue(tool.objectImplements(dc, getDottedName(IDublinCore)))

    def testAImplements(self):
        tool = self._makeOne()
        a = A()
        self.assertTrue(tool.objectImplements(a, getDottedName(IContentish)))
        self.assertTrue(tool.objectImplements(a, getDottedName(IDublinCore)))
        self.assertFalse(tool.objectImplements(a, getDottedName(IMyPortalContent)))

    def testBImplements(self):
        tool = self._makeOne()
        b = B()
        self.assertTrue(tool.objectImplements(b, getDottedName(IContentish)))
        self.assertTrue(tool.objectImplements(b, getDottedName(IDublinCore)))
        self.assertTrue(
                tool.objectImplements(b, getDottedName(IMyPortalContent)))
