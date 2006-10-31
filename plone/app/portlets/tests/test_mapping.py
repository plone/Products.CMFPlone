from Acquisition import aq_base
from Testing.ZopeTestCase import user_name

from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setSite, setHooks

from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import NotFound
from zope.app.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from plone.portlets.constants import USER_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.storage import CurrentUserAssignmentMapping
from plone.app.portlets.portlets import classic

from plone.app.portlets.browser.adding import PortletAdding

from plone.app.portlets.tests.base import PortletsTestCase

class TestNameChooser(PortletsTestCase):

    def testNameChooser(self):
        mapping = PortletAssignmentMapping()
        chooser = INameChooser(mapping)
        c = classic.Assignment()
        mapping[chooser.chooseName(None, c)] = c
        self.failUnless(c.__name__)
        d = classic.Assignment()
        self.failIfEqual(chooser.chooseName(None, d), c.__name__)

class TestContextMapping(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        self.manager = getUtility(IPortletManager, name=u'plone.leftcolumn')

    def testAdapting(self):
        mapping = getMultiAdapter((self.folder, self.manager,), IPortletAssignmentMapping)
        self.assertEquals(0, len(mapping))

    def testEquivalence(self):
        mapping = getMultiAdapter((self.folder, self.manager,), IPortletAssignmentMapping)
        c = classic.Assignment()
        mapping['foo'] = c

        mapping2 = getMultiAdapter((self.folder, self.manager,), IPortletAssignmentMapping)
        self.assertEquals(mapping2['foo'], c)

class TestTraverser(PortletsTestCase):

    def afterSetUp(self):
        self.mapping = PortletAssignmentMapping()
        c = classic.Assignment()
        self.mapping['foo'] = c
        self.traverser = getMultiAdapter((self.mapping, self.folder.REQUEST), IBrowserPublisher)

    def testTraverseToName(self):
        obj = self.traverser.publishTraverse(self.folder.REQUEST, 'foo')
        self.failUnless(aq_base(obj) is self.mapping['foo'])
        self.failUnless(obj.aq_parent is self.mapping)

    def testTraverseToView(self):
        view = self.traverser.publishTraverse(self.folder.REQUEST, '+')
        self.failUnless(isinstance(view, PortletAdding))
        self.failUnless(view.aq_parent is self.mapping)

    def testTraverseToNonExistent(self):
        self.assertRaises(NotFound, self.traverser.publishTraverse, self.folder.REQUEST, 'bar')

class TestCurrentUserAssignmentMapping(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)
        manager = getUtility(IPortletManager, name='plone.leftcolumn')
        self.cat = manager[USER_CATEGORY]
        self.cat[user_name] = PortletAssignmentMapping()
        self.mapping = CurrentUserAssignmentMapping(self.portal, self.cat)

    def testKeys(self):
        self.assertEquals(0, len(self.mapping.keys()))
        assignment = classic.Assignment()
        self.cat[user_name]['foo'] = assignment
        self.assertEquals(['foo'], sorted(self.mapping.keys()))

    def testIter(self):
        a1 = classic.Assignment()
        a2 = classic.Assignment()
        self.cat[user_name]['foo'] = a1
        self.cat[user_name]['bar'] = a2
        items = [a for a in self.mapping]
        self.assertEquals(items, ['foo', 'bar'])

    def testGetItem(self):
        assignment = classic.Assignment()
        self.cat[user_name]['foo'] = assignment
        self.assertEquals(assignment, self.mapping.get('foo'))
        self.assertEquals(None, self.mapping.get('bar', None))

    def testValues(self):
        a1 = classic.Assignment()
        a2 = classic.Assignment()
        self.cat[user_name]['foo'] = a1
        self.cat[user_name]['bar'] = a2
        items = [a for a in self.mapping.values()]
        self.assertEquals(items, [a1, a2])

    def testLen(self):
        self.assertEquals(0, len(self.mapping))
        self.cat[user_name]['foo'] = classic.Assignment()
        self.assertEquals(1, len(self.mapping))

    def testItems(self):
        a1 = classic.Assignment()
        a2 = classic.Assignment()
        self.cat[user_name]['foo'] = a1
        self.cat[user_name]['bar'] = a2
        self.assertEquals([('foo', a1), ('bar', a2)], self.mapping.items())

    def testContains(self):
        self.failIf('foo' in self.mapping)
        self.cat[user_name]['foo'] = classic.Assignment()
        self.failUnless('foo' in self.mapping)

    def testHasKey(self):
        self.failIf(self.mapping.has_key('foo'))
        self.cat[user_name]['foo'] = classic.Assignment()
        self.failUnless(self.mapping.has_key('foo'))

    def testSetItem(self):
        assignment = classic.Assignment()
        self.mapping['foo'] = assignment
        self.failUnless(self.cat[user_name]['foo'] is assignment)

    def testDelItem(self):
        self.cat[user_name]['foo'] = classic.Assignment()
        del self.mapping['foo']
        self.assertEquals(0, len(self.cat[user_name]))

    def testUpdateOrder(self):
        a1 = classic.Assignment()
        a2 = classic.Assignment()
        self.cat[user_name]['foo'] = a1
        self.cat[user_name]['bar'] = a2
        self.mapping.updateOrder(['bar', 'foo'])
        self.assertEquals([('bar', a2), ('foo', a1)], self.mapping.items())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContextMapping))
    suite.addTest(makeSuite(TestTraverser))
    suite.addTest(makeSuite(TestNameChooser))
    suite.addTest(makeSuite(TestCurrentUserAssignmentMapping))
    return suite
