#
# Tests portal creation
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase


class TestPortalCreation(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        # The portal has already been set up, so there 
        # is little to do.
        pass

    def testPloneSkins(self):
        '''Plone skins should have been set up'''
        assert hasattr(self.folder, 'plone_powered.gif')

    def testDefaultView(self):
        '''index_html should render (slow test)'''
        self.portal.index_html()

            
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestPortalCreation))
        return suite

