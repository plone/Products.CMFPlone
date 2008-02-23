from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite

from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import events
from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase

class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        self.assertEquals(portlet.addview, 'portlets.Events')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_] 
        registered_interfaces.sort() 
        self.assertEquals(['plone.app.portlets.interfaces.IColumn',
          'plone.app.portlets.interfaces.IDashboard'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = events.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Events')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], events.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = events.Assignment(count=5)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, events.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = events.Assignment(count=5)

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, events.Renderer))

class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        # Make sure Events use simple_publication_workflow
        self.portal.portal_workflow.setChainForPortalTypes(['Event'], ['simple_publication_workflow'])

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or events.Assignment(template='portlet_recent', macro='portlet')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_published_events(self):
        self.setRoles(('Manager',))
        self.portal.invokeFactory('Event', 'e1')
        self.portal.invokeFactory('Event', 'e2')
        self.portal.portal_workflow.doActionFor(self.portal.e1, 'publish')
        
        r = self.renderer(assignment=events.Assignment(count=5, state=('draft',)))
        self.assertEquals(0, len(r.published_events()))
        r = self.renderer(assignment=events.Assignment(count=5, state=('published', )))
        self.assertEquals(1, len(r.published_events()))
        r = self.renderer(assignment=events.Assignment(count=5, state=('published', 'private',)))
        self.assertEquals(2, len(r.published_events()))

    def test_all_events_link(self):
        r = self.renderer(assignment=events.Assignment(count=5))
        self.failUnless(r.all_events_link().endswith('/events'))
        self.portal._delObject('events')
        r = self.renderer(assignment=events.Assignment(count=5))
        self.failUnless(r.all_events_link().endswith('/events_listing'))
        
    def test_prev_events_link(self):
        r = self.renderer(assignment=events.Assignment(count=5))
        self.failUnless(r.prev_events_link().endswith(
            '/events/aggregator/previous'))

        self.loginAsPortalOwner()
        self.portal._delObject('events')
        self.portal.invokeFactory('Folder', 'events')
        self.portal.events.invokeFactory('Folder', 'previous')
        r = self.renderer(assignment=events.Assignment(count=5))
        self.failUnless(r.prev_events_link().endswith(
            '/events/previous'))

        self.portal._delObject('events')
        r = self.renderer(assignment=events.Assignment(count=5))
        self.assertEquals(None, r.prev_events_link())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
