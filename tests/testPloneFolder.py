#
# PloneFolder tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

try: from zExceptions import NotFound
except ImportError: NotFound = 'NotFound'


class TestPloneFolder(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        pass

    def testGetObjectPosition(self):
        self.assertEqual(self.folder.getObjectPosition('.personal'), 0)

    def testGetObjectPositionRaisesNotFound(self):
        self.assertRaises(NotFound, self.folder.getObjectPosition, 'foobar')


if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestPloneFolder))
        return suite
