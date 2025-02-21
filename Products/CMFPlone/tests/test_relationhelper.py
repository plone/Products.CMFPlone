from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.relationhelper import get_relations_stats
from Products.CMFPlone.relationhelper import rebuild_relations
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified

import unittest


class TestRelationhelper(unittest.TestCase):
    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ("Manager",))

    def test_relations_stats(self):
        doc1 = self._create_content(
            type="Document", title="doc1", container=self.portal
        )
        doc2 = self._create_content(
            type="Document", title="doc2", container=self.portal
        )
        self._create_relation(doc1, doc2, "relatedItems")

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 1})
        self.assertEqual(dict(broken), {})

    def test_relations_stats_broken(self):
        doc1 = self._create_content(
            type="Document", title="doc1", container=self.portal
        )
        doc2 = self._create_content(
            type="Document", title="doc2", container=self.portal
        )
        self._create_relation(doc1, doc2, "relatedItems")
        self.portal._delObject("doc2")

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {})
        self.assertEqual(dict(broken), {"relatedItems": 1})

    def test_rebuild_relations(self):
        doc1 = self._create_content(
            type="Document", title="doc1", container=self.portal
        )
        doc2 = self._create_content(
            type="Document", title="doc2", container=self.portal
        )
        doc3 = self._create_content(
            type="Document", title="doc3", container=self.portal
        )
        intids = getUtility(IIntIds)
        doc1_intid = intids.getId(doc1)
        doc2_intid = intids.getId(doc2)
        doc3_intid = intids.getId(doc3)

        self._create_relation(doc1, doc2, "relatedItems")
        self._create_relation(doc1, doc3, "relatedItems")

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 2})
        self.assertEqual(dict(broken), {})

        rebuild_relations()

        # Relations are the same after a rebuild.
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 2})
        self.assertEqual(dict(broken), {})

        # intids are not changed.
        doc1_intid_after = intids.getId(doc1)
        doc2_intid_after = intids.getId(doc2)
        doc3_intid_after = intids.getId(doc3)
        self.assertEqual(doc1_intid, doc1_intid_after)
        self.assertEqual(doc2_intid, doc2_intid_after)
        self.assertEqual(doc3_intid, doc3_intid_after)

        # Break a relation by target.
        self.portal._delObject("doc2")

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 1})
        self.assertEqual(dict(broken), {"relatedItems": 1})

        # Broken relations are removed after rebuilding.
        rebuild_relations()
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 1})
        self.assertEqual(dict(broken), {})

        # Break a relation by source.
        self.portal._delObject("doc1")

        # Broken relation is removed. No rebuild necessary.
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {})
        self.assertEqual(dict(broken), {})

    def test_rebuild_relations_with_intid_flush(self):
        doc1 = self._create_content(
            type="Document", title="doc1", container=self.portal
        )
        doc2 = self._create_content(
            type="Document", title="doc2", container=self.portal
        )
        doc3 = self._create_content(
            type="Document", title="doc3", container=self.portal
        )
        intids = getUtility(IIntIds)
        doc1_intid = intids.getId(doc1)
        doc2_intid = intids.getId(doc2)
        doc3_intid = intids.getId(doc3)

        self._create_relation(doc1, doc2, "relatedItems")
        self._create_relation(doc1, doc3, "relatedItems")

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 2})
        self.assertEqual(dict(broken), {})

        rebuild_relations(flush_and_rebuild_intids=True)

        # Relations are the same after a rebuild.
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 2})
        self.assertEqual(dict(broken), {})

        # intids are now changed.
        doc1_intid_after = intids.getId(doc1)
        doc2_intid_after = intids.getId(doc2)
        doc3_intid_after = intids.getId(doc3)
        self.assertNotEqual(doc1_intid, doc1_intid_after)
        self.assertNotEqual(doc2_intid, doc2_intid_after)
        self.assertNotEqual(doc3_intid, doc3_intid_after)

        # Break a relation.
        self.portal._delObject("doc2")

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 1})
        self.assertEqual(dict(broken), {"relatedItems": 1})

        # Broken relations are gone after rebuilding.
        rebuild_relations(flush_and_rebuild_intids=True)
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {"relatedItems": 1})
        self.assertEqual(dict(broken), {})

    def _create_content(self, type, title, container):
        # Create a temporary id if the id is not given
        content_id = title
        container.invokeFactory(type, content_id)
        content = container[content_id]
        return content

    def _create_relation(self, source, target, relationship):
        intids = getUtility(IIntIds)
        to_id = intids.getId(target)
        from_attribute = relationship

        existing_relations = getattr(source, from_attribute, None) or []
        existing_relations.append(RelationValue(to_id))
        setattr(source, from_attribute, existing_relations)
        modified(source)
