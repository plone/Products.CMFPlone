from zope.component import getUtility, getMultiAdapter
from zope.site.hooks import setHooks, setSite

from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import news
from plone.app.portlets.storage import PortletAssignmentMapping

from plone.app.portlets.tests.base import PortletsTestCase


class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.setRoles(('Manager', ))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.News')
        self.assertEquals(portlet.addview, 'portlets.News')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.News')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(['plone.app.portlets.interfaces.IColumn',
          'plone.app.portlets.interfaces.IDashboard'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = news.Assignment(count=5)
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.News')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], news.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = news.Assignment(count=5)
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, news.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = news.Assignment(count=5)

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, news.Renderer))


class TestRenderer(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        # Make sure News Items use simple_publication_workflow
        self.portal.portal_workflow.setChainForPortalTypes(['News Item'], ['simple_publication_workflow'])

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.leftcolumn', context=self.portal)
        assignment = assignment or news.Assignment(template='portlet_recent', macro='portlet')

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_published_news_items(self):
        self.setRoles(('Manager', ))
        self.portal.invokeFactory('News Item', 'n1')
        self.portal.invokeFactory('News Item', 'n2')
        self.portal.portal_workflow.doActionFor(self.portal.n1, 'publish')

        r = self.renderer(assignment=news.Assignment(count=5, state=('draft', )))
        self.assertEquals(0, len(r.published_news_items()))
        r = self.renderer(assignment=news.Assignment(count=5, state=('published', )))
        self.assertEquals(1, len(r.published_news_items()))
        r = self.renderer(assignment=news.Assignment(count=5, state=('published', 'private', )))
        self.assertEquals(2, len(r.published_news_items()))

    def test_all_news_link(self):
        if 'news' in self.portal:
            self.portal._delObject('news')
        r = self.renderer(assignment=news.Assignment(count=5))
        self.assertEqual(r.all_news_link(), None)
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'news')
        self.failUnless(r.all_news_link().endswith('/news'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
