from Acquisition import aq_base

from zope.component import getUtility, getMultiAdapter

from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces import NotFound
from zope.app.container.interfaces import INameChooser

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.portlets.classic import ClassicPortletAssignment

from plone.app.portlets.browser.adding import PortletAdding

from plone.app.portlets.tests.base import PortletsTestCase

class TestNameChooser(PortletsTestCase):
    
    def testNameChooser(self):
        mapping = PortletAssignmentMapping()
        chooser = INameChooser(mapping)
        c = ClassicPortletAssignment()
        mapping[chooser.chooseName(None, c)] = c
        self.failUnless(c.__name__)
        d = ClassicPortletAssignment()
        self.failIfEqual(chooser.chooseName(None, d), c.__name__)

class TestContextMapping(PortletsTestCase):

    def afterSetUp(self):
        self.manager = getUtility(IPortletManager, name=u'plone.leftcolumn', context=self.portal)
        
    def testAdapting(self):
        mapping = getMultiAdapter((self.folder, self.manager,), IPortletAssignmentMapping)
        self.assertEquals(0, len(mapping))
        
    def testEquivalence(self):
        mapping = getMultiAdapter((self.folder, self.manager,), IPortletAssignmentMapping)
        c = ClassicPortletAssignment()
        mapping['foo'] = c
        
        mapping2 = getMultiAdapter((self.folder, self.manager,), IPortletAssignmentMapping)
        self.assertEquals(mapping2['foo'], c)

class TestTraverser(PortletsTestCase):
    
    def afterSetUp(self):
        self.mapping = PortletAssignmentMapping()
        c = ClassicPortletAssignment()
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
    
    def testKeys(self):
        self.fail('Testing missing')    

    def testIter(self):
        self.fail('Testing missing')
        
    def testGetItem(self):
        self.fail('Testing missing')    
    
    def testValues(self):
        self.fail('Testing missing')
        
    def testLen(self):
        self.fail('Testing missing')
    
    def testItems(self):
        self.fail('Testing missing')    

    def testContains(self): 
        self.fail('Test missing')
    
    def testHasKey(self): 
        self.fail('Test missing')

    def testSetItem(self): 
        self.fail('Test missing')

    def testDelItem(self): 
        self.fail('Test missing')

    def testUpdateOrder(self): 
        self.fail('Test missing')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContextMapping))
    suite.addTest(makeSuite(TestTraverser))
    suite.addTest(makeSuite(TestNameChooser))
    suite.addTest(makeSuite(TestCurrentUserAssignmentMapping))
    return suite
