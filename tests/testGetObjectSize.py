#
# Test the getObjSize script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base


class TestGetObjSize(PloneTestCase.PloneTestCase):

    def testGetObjSizeKBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 5678), "5.5 kB")

    def testGetObjSizeMBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 3307520), "3.2 MB")

    def testGetObjSizeGBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 7564738298), "7.0 GB")

    def testGetObjSizeKBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 5678.5), "5.5 kB")

    def testGetObjSizeMBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 3307520.5), "3.2 MB")

    def testGetObjSizeGBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 7564738298.5), "7.0 GB")

    def testGetObjSizeNone(self):
        self.assertEqual(self.portal.getObjSize(None, None), "0 kB")

    def testGetObjSizeEmptyString(self):
        self.assertEqual(self.portal.getObjSize(None, ''), "0 kB")

    def testGetObjSizeNotIntString(self):
        self.assertEqual(self.portal.getObjSize(None, 'barney'), 'barney')

    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetObjSize))
    return suite

if __name__ == '__main__':
    framework()
