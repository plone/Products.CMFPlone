#
# Test the getObjSize script
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy


class TestGetObjSize(PloneTestCase.PloneTestCase):

    def testZeroInt(self):
        self.assertEqual(self.portal.getObjSize(None, 0), "0 kB")

    def testBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 234), "1 kB")

    def testKBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 5678), "5.5 kB")

    def testMBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 3307520), "3.2 MB")

    def testGBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 7564738298), "7.0 GB")

    def testZeroFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 0.0), "0 kB")

    def testBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 234.5), "1 kB")

    def testKBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 5678.5), "5.5 kB")

    def testMBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 3307520.5), "3.2 MB")

    def testGBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 7564738298.5), "7.0 GB")

    def testNone(self):
        self.assertEqual(self.portal.getObjSize(None, None), "0 kB")

    def testEmptyString(self):
        self.assertEqual(self.portal.getObjSize(None, ''), "0 kB")

    def testNonIntString(self):
        self.assertEqual(self.portal.getObjSize(None, 'barney'), 'barney')


class TestGetObjSizedItem(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.ob = dummy.SizedItem()

    def testZero(self):
        self.ob.set_size(0)
        self.assertEquals(self.portal.getObjSize(self.ob), '0 kB')

    def testBInt(self):
        self.ob.set_size(884)
        self.assertEquals(self.portal.getObjSize(self.ob), '1 kB')

    def testKBInt(self):
        self.ob.set_size(1348)
        self.assertEquals(self.portal.getObjSize(self.ob), '1.3 kB')

    def testMBInt(self):
        self.ob.set_size(1024*1024+1024*687)
        self.assertEquals(self.portal.getObjSize(self.ob), '1.7 MB')

    def testGBInt(self):
        self.ob.set_size(1024*1024*1024+1024*1024*107)
        self.assertEquals(self.portal.getObjSize(self.ob), '1.1 GB')

    def testGBFloat(self):
        self.ob.set_size(float(1024*1024*1024+1024*1024*107))
        self.assertEquals(self.portal.getObjSize(self.ob), '1.1 GB')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetObjSize))
    suite.addTest(makeSuite(TestGetObjSizedItem))
    return suite
