#
# ActionsTool tests
#

from Products.CMFPlone.tests import PloneTestCase

from traceback import format_exception
from zope.i18nmessageid.message import Message

from Acquisition import Explicit
from OFS.SimpleItem import Item
from Products.CMFPlone.PloneBatch import Batch


class TestBatch(PloneTestCase.PloneTestCase):

    def testBatch(self):
        sequence = range(1000)
        batch = Batch(sequence, size=10, start=10)
        self.assertEqual([b for b in batch], [10, 11, 12, 13, 14, 15, 16, 17, 18, 19])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBatch))
    return suite
