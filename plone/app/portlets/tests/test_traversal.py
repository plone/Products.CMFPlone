from Acquisition import aq_parent
from Testing.ZopeTestCase import user_name

from zope.app.component.hooks import setSite, setHooks
from zope.component import getMultiAdapter, getUtility

from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY

from plone.app.portlets.tests.base import PortletsTestCase
from plone.app.portlets.portlets import classic

class TestTraversal(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def testContextNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        mapping = self.folder.restrictedTraverse('++contextportlets++plone.leftcolumn')
        target = getMultiAdapter((self.folder, manager), IPortletAssignmentMapping)
        self.failUnless(aq_parent(mapping) is self.folder)
        mapping['foo'] = assignment
        self.failUnless(target['foo'] is assignment)
        self.assertEquals('++contextportlets++plone.leftcolumn', mapping.id)

    def testDashboardNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.dashboard1')
        mapping = self.portal.restrictedTraverse('++dashboard++plone.dashboard1+' + user_name)
        self.failUnless(aq_parent(mapping) is self.portal)
        mapping['foo'] = assignment
        self.failUnless(manager[USER_CATEGORY][user_name]['foo'] is assignment)
        self.assertEquals('++dashboard++plone.dashboard1+' + user_name, mapping.id)

    def testGroupNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        mapping = self.portal.restrictedTraverse('++groupportlets++plone.leftcolumn+Reviewers')
        self.failUnless(aq_parent(mapping) is self.portal)
        mapping['foo'] = assignment
        self.failUnless(manager[GROUP_CATEGORY]['Reviewers']['foo'] is assignment)
        self.assertEquals('++groupportlets++plone.leftcolumn+Reviewers', mapping.id)

    def testContentTypeNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        mapping = self.portal.restrictedTraverse('++contenttypeportlets++plone.leftcolumn+Image')
        self.failUnless(aq_parent(mapping) is self.portal)
        mapping['foo'] = assignment
        self.failUnless(manager[CONTENT_TYPE_CATEGORY]['Image']['foo'] is assignment)
        self.assertEquals('++contenttypeportlets++plone.leftcolumn+Image', mapping.id)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTraversal))
    return suite
