from plone.app.portlets.tests.base import PortletsTestCase

class TestProductInstall(PortletsTestCase):

    def testTestsRun(self):
        self.assertEquals(True, True)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestProductInstall))
    return suite
