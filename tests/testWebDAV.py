import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.utils import getToolByName

# Python 2.1 compatibility
def mkdict(items):
    '''Constructs a dict from a sequence of (key, value) pairs.'''
    d = {}
    for k, v in items:
        d[k] = v
    return d


class TestDAVProperties(PloneTestCase.PloneTestCase):

    def testPropertiesToolTitle(self):
        ptool = getToolByName(self.portal, 'portal_properties')
        psets = mkdict(ptool.propertysheets.items())
        self.failUnless('default' in psets)
        default = psets['default']
        items = mkdict(default.propertyItems())
        self.failUnless('title' in items.keys())
        self.assertEquals(items['title'], self.portal.title)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDAVProperties))
    return suite

if __name__ == '__main__':
    framework()
