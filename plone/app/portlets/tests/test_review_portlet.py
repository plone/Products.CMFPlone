from zope.component import getUtility, getMultiAdapter
from zope.site.hooks import setHooks, setSite

from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.utils import _getDottedName

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.portlets import review

from plone.app.portlets.tests.base import PortletsTestCase


class TestPortlet(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.setRoles(('Manager', ))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='portlets.Review')
        self.assertEquals(portlet.addview, 'portlets.Review')

    def testRegisteredInterfaces(self):
        portlet = getUtility(IPortletType, name='portlets.Review')
        registered_interfaces = [_getDottedName(i) for i in portlet.for_]
        registered_interfaces.sort()
        self.assertEquals(['plone.app.portlets.interfaces.IColumn',
          'plone.app.portlets.interfaces.IDashboard'],
          registered_interfaces)

    def testInterfaces(self):
        portlet = review.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='portlets.Review')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # This is a NullAddForm - calling it does the work
        addview()

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], review.Assignment))

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
        self.setRoles(('Manager'), )
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.portal_membership.getMemberById('test_user_1_').setMemberProperties(
                                    {'fullname': 'Test user'})

        # add Folder and assign Reviewer role to our Test user there
        self.portal.invokeFactory('Folder', 'folder1')
        self.folder1 = self.portal.folder1
        self.folder1.manage_setLocalRoles('test_user_1_', ['Reviewer'])
        self.folder1.reindexObjectSecurity()

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
        wf = getToolByName(self.portal, 'portal_workflow')
        wf.doActionFor(self.portal.doc1, 'submit')
        r = self.renderer(assignment=review.Assignment())
        self.assertEquals(1, len(r.review_items()))
        self.assertEquals(r.review_items()[0]['creator'], "Test user")

    def test_full_news_link(self):
        r = self.renderer(assignment=review.Assignment())
        self.failUnless(r.full_review_link().endswith('/full_review_list'))

    def test_full_news_link_local_reviewer(self):
        # login as our test user
        self.login('test_user_1_')
        self.setRoles(['Member'])

        # there should be no full news link on site root for our local reviewer
        r = self.renderer(assignment=review.Assignment())
        self.failIf(r.full_review_link())

        # get renderer in context of our reviewer's folder
        r = self.renderer(context=self.folder1, assignment=review.Assignment())
        self.assertEqual(r.full_review_link(), '%s/full_review_list' %
            self.folder1.absolute_url())

    def test_title(self):
        r = self.renderer(assignment=review.Assignment())
        self.assertEquals(str(r.title), 'box_review_list')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
