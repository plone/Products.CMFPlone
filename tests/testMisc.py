#!/usr/bin/python
#$Id: testMisc.py,v 1.1 2004/01/15 20:28:20 zopezen Exp $

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
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestMisc))
        return suite
