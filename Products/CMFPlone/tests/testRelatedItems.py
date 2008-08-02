#
# Tests the related items support
#

from Products.CMFPlone.tests import PloneTestCase


class TestRelatedItems(PloneTestCase.PloneTestCase):

    def testRelatedItems(self):
        # create two objects
        self.folder.invokeFactory('Document', id='obj1', title='Obj1')
        obj1 = self.folder.obj1
        self.folder.invokeFactory('Document', id='obj2', title='Obj2')
        obj2 = self.folder.obj2

        # relate them
        obj1.setRelatedItems([obj2.UID()])

        # call the script for retrieving the items
        related = obj1.computeRelatedItems()

        # check length
        self.assertEqual(len(related), 1)

        # check object
        self.assertEqual(related[0], obj2)

    def testNoRelatedItems(self):
        self.folder.invokeFactory('Document', id='obj1', title='Obj1')
        related = self.folder.obj1.computeRelatedItems()
        self.assertEqual(len(related), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRelatedItems))
    return suite
