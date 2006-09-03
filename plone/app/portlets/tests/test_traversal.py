from plone.app.portlets.tests.base import PortletsTestCase

class TestTraversal(PortletsTestCase):

    def testContextNamespace(self): 
        self.fail('Test missing')

    def testCurrentUserNamespace(self): 
        self.fail('Test missing')

    def testUserNamespace(self): 
        self.fail('Test missing')

    def testGroupNamespace(self): 
        self.fail('Test missing')

    def testContentTypeNamespace(self): 
        self.fail('Test missing')
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTraversal))
    return suite
