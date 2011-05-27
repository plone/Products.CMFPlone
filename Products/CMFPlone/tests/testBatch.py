from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.tests import PloneTestCase


class TestBatch(PloneTestCase.PloneTestCase):

    def test_batch(self):
        sequence = range(1000)
        batch = Batch(sequence, size=10, start=10)
        self.assertEqual([b for b in batch],
            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
