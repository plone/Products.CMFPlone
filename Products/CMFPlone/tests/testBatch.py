import unittest

from Products.CMFPlone.PloneBatch import Batch


class TestBatch(unittest.TestCase):

    def test_batch_no_lazy(self):
        batch = Batch(range(100), size=10, start=10)
        self.assertEqual([b for b in batch],
            [10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
