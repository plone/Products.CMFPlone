#
# Skeleton PloneTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

ZopeTestCase.installProduct('SomeProduct')


class TestSomeProduct(PloneTestCase.PloneTestCase):

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

