from persistent.list import PersistentList
from plone.app.testing import TEST_USER_ID, setRoles
from Products.CMFPlone.controlpanel.browser.relations import get_relations_stats
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from z3c.relationfield import RelationValue
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified

import unittest


class TestRelationsControlpanel(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ('Manager',))

    def test_relations_stats(self):
        self.portal.invokeFactory('Document', id='doc1', title='doc1')
        doc1 = self.portal['doc1']
        self.portal.invokeFactory('Document', id='doc2', title='doc2')
        doc2 = self.portal['doc2']
        intids = getUtility(IIntIds)
        doc1.relatedItems = PersistentList()
        doc1.relatedItems.append(RelationValue(intids.getId(doc2)))
        modified(doc1)
        # TODO: simplify when relation-support is merged into plone.api
        # api.relation.create(doc1, doc2, 'relatedItems')

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 1})
        self.assertEqual(dict(broken), {})
        view = getMultiAdapter((self.portal, self.request), name='inspect-relations')
        self.assertTrue(view())
        self.assertTrue(view(relation='relatedItems'))

    def test_relations_stats_broken(self):
        self.portal.invokeFactory('Document', id='doc1', title='doc1')
        doc1 = self.portal['doc1']
        self.portal.invokeFactory('Document', id='doc2', title='doc2')
        doc2 = self.portal['doc2']
        self.portal.invokeFactory('Document', id='doc3', title='doc3')
        doc3 = self.portal['doc3']

        intids = getUtility(IIntIds)
        doc1.relatedItems = PersistentList()
        doc1.relatedItems.append(RelationValue(intids.getId(doc2)))
        doc1.relatedItems.append(RelationValue(intids.getId(doc3)))
        modified(doc1)
        # api.relation.create(doc1, doc2, 'relatedItems')
        # api.relation.create(doc1, doc3, 'relatedItems')

        self.portal._delObject('doc2')
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 1})
        self.assertEqual(dict(broken), {'relatedItems': 1})
        view = getMultiAdapter((self.portal, self.request), name='inspect-relations')
        self.assertTrue(view())
        self.assertTrue(view(relation='relatedItems'))

    def test_rebuild_relations(self):
        self.portal.invokeFactory('Document', id='doc1', title='doc1')
        doc1 = self.portal['doc1']
        self.portal.invokeFactory('Document', id='doc2', title='doc2')
        doc2 = self.portal['doc2']
        self.portal.invokeFactory('Document', id='doc3', title='doc3')
        doc3 = self.portal['doc3']
        intids = getUtility(IIntIds)
        doc1_intid = intids.getId(doc1)
        doc2_intid = intids.getId(doc2)
        doc3_intid = intids.getId(doc3)

        doc1.relatedItems = PersistentList()
        doc1.relatedItems.append(RelationValue(doc2_intid))
        doc1.relatedItems.append(RelationValue(doc3_intid))
        modified(doc1)
        # api.relation.create(doc1, doc2, 'relatedItems')
        # api.relation.create(doc1, doc3, 'relatedItems')

        # Make sure the catalog index queue is flushed.
        self.portal.portal_catalog.searchResults({})

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 2})
        self.assertEqual(dict(broken), {})

        view = getMultiAdapter((self.portal, self.request), name='rebuild-relations')
        results = view(rebuild=True)

        # relations are the same after a rebuild
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 2})
        self.assertEqual(dict(broken), {})

        # intids are not changed
        doc1_intid_after = intids.getId(doc1)
        doc2_intid_after = intids.getId(doc2)
        doc3_intid_after = intids.getId(doc3)
        self.assertEqual(doc1_intid, doc1_intid_after)
        self.assertEqual(doc2_intid, doc2_intid_after)
        self.assertEqual(doc3_intid, doc3_intid_after)

        # break a relation
        self.portal._delObject('doc2')

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 1})
        self.assertEqual(dict(broken), {'relatedItems': 1})

        # broken relations are gone after rebuilding
        view = getMultiAdapter((self.portal, self.request), name='rebuild-relations')
        results = view(rebuild=True)
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 1})
        self.assertEqual(dict(broken), {})

    def test_rebuild_relations_with_intid(self):
        self.portal.invokeFactory('Document', id='doc1', title='doc1')
        doc1 = self.portal['doc1']
        self.portal.invokeFactory('Document', id='doc2', title='doc2')
        doc2 = self.portal['doc2']
        self.portal.invokeFactory('Document', id='doc3', title='doc3')
        doc3 = self.portal['doc3']
        intids = getUtility(IIntIds)
        doc1_intid = intids.getId(doc1)
        doc2_intid = intids.getId(doc2)
        doc3_intid = intids.getId(doc3)
        doc1.relatedItems = PersistentList()
        doc1.relatedItems.append(RelationValue(doc2_intid))
        doc1.relatedItems.append(RelationValue(doc3_intid))
        modified(doc1)
        # api.relation.create(doc1, doc2, 'relatedItems')
        # api.relation.create(doc1, doc3, 'relatedItems')

        # Make sure the catalog index queue is flushed.
        self.portal.portal_catalog.searchResults({})

        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 2})
        self.assertEqual(dict(broken), {})

        view = getMultiAdapter((self.portal, self.request), name='rebuild-relations')
        results = view(rebuild=True, flush_and_rebuild_intids=True)

        # relations are the same after a rebuild
        stats, broken = get_relations_stats()
        self.assertEqual(dict(stats), {'relatedItems': 2})
        self.assertEqual(dict(broken), {})

        # intids are now changed
        doc1_intid_after = intids.getId(doc1)
        doc2_intid_after = intids.getId(doc2)
        doc3_intid_after = intids.getId(doc3)
        self.assertNotEqual(doc1_intid, doc1_intid_after)
        self.assertNotEqual(doc2_intid, doc2_intid_after)
        self.assertNotEqual(doc3_intid, doc3_intid_after)
