from zope.component import getUtility, getMultiAdapter, queryMultiAdapter
from zope.app.component.hooks import setHooks, setSite

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import login

from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase

class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Login')
        self.assertEquals(portlet.addview, 'portlets.Login')

    def testInterfaces(self):
        portlet = login.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Login')
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        adding = getMultiAdapter((mapping, request,), name='+')
        addview = getMultiAdapter((adding, request), name=portlet.addview)

        # This is a NullAddForm - calling it does the work
        addview()

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], login.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = login.Assignment()
        editview = queryMultiAdapter((mapping['foo'], request), name='edit.html', default=None)
        self.failUnless(editview is None)

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = login.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, login.Renderer))

class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or login.Assignment()

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def testAvailable(self):
        r = self.renderer()
        self.assertEquals(True, r.available())
        self.portal.acl_users._delObject('credentials_cookie_auth')
        r = self.renderer()
        self.assertEquals(False, r.available())

    def testShow(self):
        request = self.folder.REQUEST
        
        r = self.renderer()
        self.assertEquals(False, r.show())
        
        self.logout()
        
        del request.__annotations__
        self.assertEquals(True, r.show())
        
        del request.__annotations__
        request['URL'] = self.portal.absolute_url() + '/login_form'
        self.assertEquals(False, self.renderer(request=request).show())

        del request.__annotations__
        request['URL'] = self.portal.absolute_url() + '/join_form'
        self.assertEquals(False, self.renderer(request=request).show())

    # TODO: Add more detailed tests here

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
