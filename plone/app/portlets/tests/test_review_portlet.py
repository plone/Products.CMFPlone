from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import review
from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase

class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Review')
        self.assertEquals(portlet.addview, 'portlets.Review')

    def testInterfaces(self):
        portlet = review.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Review')
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        adding = getMultiAdapter((mapping, request,), name='+')
        addview = getMultiAdapter((adding, request), name=portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], review.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = review.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit.html')
        self.failUnless(isinstance(editview, review.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = review.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, review.Renderer))

class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or review.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_review_items(self):
        r = self.renderer(assignment=review.Assignment())
        self.assertEquals(0, len(r.review_items()))

    def test_full_news_link(self):
        r = self.renderer(assignment=review.Assignment())
        self.failUnless(r.full_review_link().endswith('/full_review_list'))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
