from Products.CMFCore.utils import getToolInterface
from Products.CMFPlone.tests import PloneTestCase

class TestUtilities(PloneTestCase.PloneContentLessTestCase):
    def testToolRegistration(self):
        from Products.CMFPlone.migrations.v3_0.alphas import registration

        for (tool_id, interface) in registration:
            self.assertEqual(getToolInterface(tool_id), interface)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtilities))
    return suite
