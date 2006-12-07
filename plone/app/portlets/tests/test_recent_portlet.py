from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import recent
from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase

class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Recent')
        self.assertEquals(portlet.addview, 'portlets.Recent')

    def testInterfaces(self):
        portlet = recent.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Recent')
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        adding = getMultiAdapter((mapping, request,), name='+')
        addview = getMultiAdapter((adding, request), name=portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], recent.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = recent.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit.html')
        self.failUnless(isinstance(editview, recent.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = recent.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, recent.Renderer))

class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or recent.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_recent_items(self):
        r = self.renderer(assignment=recent.Assignment(count=5))
        self.assertEquals(5, len(r.recent_items()))

    def test_recently_modified_link(self):
        r = self.renderer(assignment=recent.Assignment(count=5))
        self.failUnless(r.recently_modified_link().endswith('/recently_modified'))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
