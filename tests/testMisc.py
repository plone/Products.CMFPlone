#!/usr/bin/python
#$Id$

# Miscellaneous tests

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base


class TestMisc(PloneTestCase.PloneTestCase):

    def testGetObjSize(self):
        assert self.portal.getObjSize(None, 3307520) == "3.15 M"

    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestMisc))
        return suite

