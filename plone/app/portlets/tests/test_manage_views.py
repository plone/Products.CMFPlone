from plone.app.portlets.tests.base import PortletsTestCase


class TestManageAssignments(PortletsTestCase):

    def testMoveUp(self):
        self.fail('Test missing')

    def testMoveDown(self):
        self.fail('Test missing')

    def testDelete(self):
        self.fail('Test missing')


def test_suite():
    from unittest import TestSuite
    #from unittest import makeSuite
    suite = TestSuite()
    # TODO: Write tests that *pass*
    #suite.addTest(makeSuite(TestManageAssignments))
    return suite
