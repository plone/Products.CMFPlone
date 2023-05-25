from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class TestBatchIntegration(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def test_batch_brains(self):
        from plone.base.batch import Batch

        portal = self.layer["portal"]
        obj_ids = ["%stest" % chr(c) for c in range(97, 123)]
        for obj_id in obj_ids:
            portal.invokeFactory("Document", obj_id)

        brains = portal.portal_catalog.searchResults(
            portal_type="Document", sort_on="id"
        )
        for start in (0, 1, 2, 10):
            batch = Batch(brains, size=0, start=start)
            self.assertEqual(
                batch[0].id, obj_ids[start], f"Failing test for start value: {start}"
            )
