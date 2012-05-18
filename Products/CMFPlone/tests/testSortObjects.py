# Tests the sortObjects script

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
        self.items2 = [
            dummy.Item('D', 'Fred'),
            dummy.Item('c', 'Wilma'),
            dummy.Item('B', 'barney'),
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

    def testSortObjectsIsCaseInsensitive(self):
        # Sorts by passed in method
        sorted = self.portal.sortObjects(self.items2, 'getId')
        self.assertEqual([x.getId() for x in sorted], ['a', 'B', 'c', 'D'])
