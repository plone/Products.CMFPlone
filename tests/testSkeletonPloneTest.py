#
# Skeleton integration test. A full-blown Plone portal is set up.
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

# Create a Plone site in the test (demo-) storage
app = ZopeTestCase.app()
PloneTestCase.setupPloneSite(app, id='portal')
ZopeTestCase.close(app)

ZopeTestCase.installProduct('SomeProduct')


class TestSomeProduct(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        ''' At this point a Plone Site is setup
            Install additional Users, Rolse, Product here'''
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

