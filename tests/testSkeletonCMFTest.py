#
# Skeleton CMF test. A CMF portal is set up.
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import CMFTestCase

ZopeTestCase.installProduct('SomeProduct')

# Create a CMF site in the test (demo-) storage
app = ZopeTestCase.app()
CMFTestCase.setupCMFSite(app, id='portal')
ZopeTestCase.close(app)


class TestSomeProduct(CMFTestCase.CMFTestCase):

    def afterSetUp(self):
        pass

    def testSomething(self):
        '''Test something'''
        self.failUnless(1==1)

            
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestSomeProduct))
        return suite

