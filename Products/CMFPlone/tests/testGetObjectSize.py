from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy


class TestGetObjSize(PloneTestCase.PloneTestCase):

    def testZeroInt(self):
        self.assertEqual(self.portal.getObjSize(None, 0), "0 KB")

    def testBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 234), "1 KB")

    def testKBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 5678), "5.5 KB")

    def testMBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 3307520), "3.2 MB")

    def testGBInt(self):
        self.assertEqual(self.portal.getObjSize(None, 7564738298), "7.0 GB")

    def testZeroFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 0.0), "0 KB")

    def testBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 234.5), "1 KB")

    def testKBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 5678.5), "5.5 KB")

    def testMBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 3307520.5), "3.2 MB")

    def testGBFloat(self):
        self.assertEqual(self.portal.getObjSize(None, 7564738298.5), "7.0 GB")

    def testNone(self):
        self.assertEqual(self.portal.getObjSize(None, None), "0 KB")

    def testEmptyString(self):
        self.assertEqual(self.portal.getObjSize(None, ''), "0 KB")

    def testNonIntString(self):
        self.assertEqual(self.portal.getObjSize(None, 'barney'), 'barney')


class TestGetObjSizedItem(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.ob = dummy.SizedItem()

    def testZero(self):
        self.ob.set_size(0)
        self.assertEqual(self.portal.getObjSize(self.ob), '0 KB')

    def testBInt(self):
        self.ob.set_size(884)
        self.assertEqual(self.portal.getObjSize(self.ob), '1 KB')

    def testKBInt(self):
        self.ob.set_size(1348)
        self.assertEqual(self.portal.getObjSize(self.ob), '1.3 KB')

    def testMBInt(self):
        self.ob.set_size(1024 * 1024 + 1024 * 687)
        self.assertEqual(self.portal.getObjSize(self.ob), '1.7 MB')

    def testGBInt(self):
        self.ob.set_size(1024 * 1024 * 1024 + 1024 * 1024 * 107)
        self.assertEqual(self.portal.getObjSize(self.ob), '1.1 GB')

    def testGBFloat(self):
        self.ob.set_size(float(1024 * 1024 * 1024 + 1024 * 1024 * 107))
        self.assertEqual(self.portal.getObjSize(self.ob), '1.1 GB')
