from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets.classic import ClassicPortletAssignment
from plone.app.portlets.portlets.classic import ClassicPortletEditForm
from plone.app.portlets.portlets.classic import ClassicPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase

class TestClassicPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Classic')
        self.assertEquals(portlet.addview, 'portlets.Classic')

    def testInterfaces(self):
        portlet = ClassicPortletAssignment(template='portlet_recent', macro='portlet')
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Classic')
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        adding = getMultiAdapter((mapping, request,), name='+')
        addview = getMultiAdapter((adding, request), name=portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], ClassicPortletAssignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = ClassicPortletAssignment(template='portlet_recent', macro='portlet')
        editview = getMultiAdapter((mapping['foo'], request), name='edit.html')
        self.failUnless(isinstance(editview, ClassicPortletEditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = ClassicPortletAssignment(template='portlet_recent', macro='portlet')

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, ClassicPortletRenderer))

class TestClassicPortletRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or ClassicPortletAssignment(template='portlet_recent', macro='portlet')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def testUseMacro(self):
        r = self.renderer(assignment=ClassicPortletAssignment(template='portlet_recent', macro='portlet'))
        self.assertEquals(True, r.use_macro())
        r = self.renderer(assignment=ClassicPortletAssignment(template='portlet_recent', macro=None))
        self.assertEquals(False, r.use_macro())

    def testPathExpression(self):
        r = self.renderer(assignment=ClassicPortletAssignment(template='portlet_recent', macro='portlet'))
        self.assertEquals('context/portlet_recent/macros/portlet', r.path_expression())
        r = self.renderer(assignment=ClassicPortletAssignment(template='portlet_recent', macro=None))
        self.assertEquals('context/portlet_recent', r.path_expression())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestClassicPortlet))
    suite.addTest(makeSuite(TestClassicPortletRenderer))
    return suite
