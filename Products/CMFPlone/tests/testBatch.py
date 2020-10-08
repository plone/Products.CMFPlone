from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from ZTUtils.Lazy import LazyMap

import unittest


class TestBatch(unittest.TestCase):

    def test_batch_no_lazy(self):
        batch = Batch(range(100), size=10, start=10)
        self.assertEqual([b for b in batch],
                         [10, 11, 12, 13, 14, 15, 16, 17, 18, 19])

    def test_batch_lazy_map(self):
        def get(key):
            return key
        sequence = LazyMap(get, range(80, 90), actual_result_count=95)
        batch = Batch(sequence, size=10, start=80)
        self.assertEqual(
            [b for b in batch],
            [80, 81, 82, 83, 84, 85, 86, 87, 88, 89])

        self.assertEqual(batch.numpages, 10)
        self.assertEqual(batch.pagenumber, 9)
        self.assertEqual(batch.navlist, range(6, 11))
        self.assertEqual(batch.leapback, [])
        self.assertEqual(batch.prevlist, range(6, 9))
        self.assertEqual(batch.previous.length, 10)
        self.assertEqual(batch.next.length, 5)
        self.assertEqual(batch.pageurl({}), 'b_start:int=80')
        self.assertListEqual(
            list(batch.prevurls({})),
            [
                (6, 'b_start:int=50'),
                (7, 'b_start:int=60'),
                (8, 'b_start:int=70'),
            ]
        )
        self.assertListEqual(
            list(batch.nexturls({})),
            [(10, 'b_start:int=90')],
        )


class TestBatchIntegration(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def test_batch_brains(self):
        portal = self.layer['portal']
        obj_ids = ['%stest' % chr(c) for c in range(97, 123)]
        for obj_id in obj_ids:
            portal.invokeFactory('Document', obj_id)

        brains = portal.portal_catalog.searchResults(portal_type='Document',
                                                     sort_on='id')
        for start in (0, 1, 2, 10):
            batch = Batch(brains, size=0, start=start)
            self.assertEqual(
                batch[0].id,
                obj_ids[start],
                f'Failing test for start value: {start}'
            )
