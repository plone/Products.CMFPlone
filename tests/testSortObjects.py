#
# Tests the sortObjects script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy


class TestSortObjects(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.items = [
            dummy.Item('d', 'fred'),
            dummy.Item('c', 'wilma'),
            dummy.Item('b', 'barney'),
            dummy.Item('a', 'betty'),
        ]

    def testSortObjectsDefault(self):
        # Sorts by title_or_id by default
        sorted = self.portal.sortObjects(self.items)
        self.assertEqual([x.getId() for x in sorted], ['b', 'a', 'd', 'c'])

    def testSortObjectById(self):
        # Sorts by passed in method
        sorted = self.portal.sortObjects(self.items, 'getId')
        self.assertEqual([x.getId() for x in sorted], ['a', 'b', 'c', 'd'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSortObjects))
    return suite

if __name__ == '__main__':
    framework()
