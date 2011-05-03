#
# CatalogTool tests
#

import unittest
import zope.interface

from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base
from DateTime import DateTime
from OFS.ObjectManager import REPLACEABLE
from Products.CMFCore.permissions import AccessInactivePortalContent
import transaction

from plone.indexer.wrapper import IndexableObjectWrapper
from Products.CMFPlone.CatalogTool import CatalogTool

from Products.CMFPlone.CatalogTool import is_folderish
from Products.CMFPlone.tests import dummy
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IAttributeUUID

from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.interface.declarations import alsoProvides

portal_name = PloneTestCase.portal_name
default_user  = PloneTestCase.default_user

user2  = 'u2'
group2 = 'g2'

base_content = ['Members', 'aggregator', 'aggregator',
                'events', 'news', default_user, 'front-page', 'doc']


class TestCatalogSetup(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

    def testSearchableTextIsZCTextIndex(self):
        # SearchableText index should be a ZCTextIndex
        itype = self.catalog.Indexes['SearchableText'].__class__.__name__
        self.assertEqual(itype, 'ZCTextIndex')

    def testDescriptionIsZCTextIndex(self):
        # Description index should be a ZCTextIndex
        itype = self.catalog.Indexes['Description'].__class__.__name__
        self.assertEqual(itype, 'ZCTextIndex')

    def testTitleIsZCTextIndex(self):
        # Title index should be a ZCTextIndex
        itype = self.catalog.Indexes['Title'].__class__.__name__
        self.assertEqual(itype, 'ZCTextIndex')

    def testPloneLexiconIsZCTextLexicon(self):
        # Lexicon should be a ZCTextIndex lexicon
        self.failUnless(hasattr(aq_base(self.catalog), 'plone_lexicon'))
        self.assertEqual(self.catalog.plone_lexicon.meta_type,\
                         'ZCTextIndex Lexicon')

    def testPathIsExtendedPathIndex(self):
        # path index should be an ExtendedPathIndex
        self.assertEqual(self.catalog.Indexes['path'].__class__.__name__,
                         'ExtendedPathIndex')

    def testGetObjPositionInParentIsGopipIndex(self):
        # getObjPositionInParent index should be a FieldIndex
        # also see TestCatalogOrdering below
        self.assertEqual(self.catalog.Indexes['getObjPositionInParent'].__class__.__name__,
                         'GopipIndex')

    def testGetObjSizeInSchema(self):
        # getObjSize column should be in catalog schema
        self.failUnless('getObjSize' in self.catalog.schema())

    def testExclude_from_navInSchema(self):
        # exclude_from_nav column should be in catalog schema
        self.failUnless('exclude_from_nav' in self.catalog.schema())

    def testIs_folderishInSchema(self):
        # is_folderish should be in catalog schema
        self.failUnless('is_folderish' in self.catalog.schema())

    def testIs_folderishIsBooleanIndex(self):
        # is_folderish should be a BooleanIndex
        self.failUnless(self.catalog.Indexes['is_folderish'].__class__.__name__,
                        'BooleanIndex')

    def testDateIsDateIndex(self):
        # Date should be a DateIndex
        self.assertEqual(self.catalog.Indexes['Date'].__class__.__name__,
                         'DateIndex')

    def testCreatedIsDateIndex(self):
        # created should be a DateIndex
        self.assertEqual(self.catalog.Indexes['created'].__class__.__name__,
                         'DateIndex')

    def testEffectiveIsDateIndex(self):
        # effective should be a DateIndex
        self.assertEqual(self.catalog.Indexes['effective'].__class__.__name__,
                         'DateIndex')

    def testEndIsDateIndex(self):
        # end should be a DateIndex
        self.assertEqual(self.catalog.Indexes['end'].__class__.__name__,
                         'DateIndex')

    def testExpiresIsDateIndex(self):
        # expires should be a DateIndex
        self.assertEqual(self.catalog.Indexes['expires'].__class__.__name__,
                         'DateIndex')

    def testModifiedIsDateIndex(self):
        # modified should be a DateIndex
        self.assertEqual(self.catalog.Indexes['modified'].__class__.__name__,
                         'DateIndex')

    def testStartIsDateIndex(self):
        # start should be a DateIndex
        self.assertEqual(self.catalog.Indexes['start'].__class__.__name__,
                         'DateIndex')

    def testEffectiveRangeIsDateRangeIndex(self):
        # effectiveRange should be a DateRangeIndex
        self.assertEqual(self.catalog.Indexes['effectiveRange'].__class__.__name__,
                         'DateRangeIndex')

    def testSortable_TitleIsFieldIndex(self):
        # sortable_title should be a FieldIndex
        self.assertEqual(self.catalog.Indexes['sortable_title'].__class__.__name__,
                         'FieldIndex')

    def testExpirationDateInSchema(self):
        # ExpirationDate column should be in catalog schema
        self.failUnless('ExpirationDate' in self.catalog.schema())

    def testExpiresDateNotInSchema(self):
        # ExpirationDate column should be in catalog schema
        self.failIf('ExpiresDate' in self.catalog.schema())

    def testIs_Default_PageIsBooleanIndex(self):
        # sortable_title should be a BooleanIndex
        self.assertEqual(self.catalog.Indexes['is_default_page'].__class__.__name__,
                         'BooleanIndex')


class TestCatalogIndexing(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', id='doc', title='Foo', description='Bar')
        self.catalog.unindexObject(self.folder.doc)

    def assertResults(self, result, expect):
        # Verifies ids of catalog results against expected ids
        lhs = [r.getId for r in result]
        lhs.sort()
        rhs = list(expect)
        rhs.sort()
        self.assertEqual(lhs, rhs)

    def testFixture(self):
        self.assertEqual(self.folder.doc.getId(), 'doc')
        self.assertEqual(self.folder.doc.Title(), 'Foo')
        self.assertEqual(self.folder.doc.Description(), 'Bar')
        self.assertEqual(len(self.catalog(getId='doc')), 0)
        self.assertEqual(len(self.catalog(Title='Foo')), 0)
        self.assertEqual(len(self.catalog(Description='Bar')), 0)

    def testIndexObject(self):
        # Object should be indexed
        self.catalog.indexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(getId='doc')), 1)
        self.assertEqual(len(self.catalog(Title='Foo')), 1)
        self.assertEqual(len(self.catalog(Description='Bar')), 1)

    def testReindexObject(self):
        # Object should be indexed
        self.catalog.reindexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(getId='doc')), 1)
        self.assertEqual(len(self.catalog(Title='Foo')), 1)
        self.assertEqual(len(self.catalog(Description='Bar')), 1)

    def testUnindexObject(self):
        # Object should be unindexed
        self.catalog.indexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(getId='doc')), 1)
        self.catalog.unindexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(getId='doc')), 0)

    def testIndexObjectUpdatesMetadata(self):
        # Indexing should update metadata
        self.catalog.indexObject(self.folder.doc)
        brain = self.catalog(getId='doc')[0]
        self.assertEqual(brain.getId, 'doc')
        self.assertEqual(brain.Title, 'Foo')
        self.assertEqual(brain.Description, 'Bar')

    def testReindexObjectUpdatesMetadata(self):
        # Reindexing should update metadata
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc)
        brain = self.catalog(getId='doc')[0]
        self.assertEqual(brain.getId, 'doc')
        self.assertEqual(brain.Title, 'Fred')
        self.assertEqual(brain.Description, 'BamBam')

    def testReindexObjectSkipsMetadata(self):
        # Reindexing should not update metadata when update_metadata=0
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc, update_metadata=0)
        brain = self.catalog(getId='doc')[0]
        # Metadata did not change
        self.assertEqual(brain.getId, 'doc')
        self.assertEqual(brain.Title, 'Foo')
        self.assertEqual(brain.Description, 'Bar')

    def testReindexTitleOnly(self):
        # Reindexing should only index the Title
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc, idxs=['Title'])
        self.assertEqual(len(self.catalog(getId='doc')), 1)
        self.assertEqual(len(self.catalog(Title='Fred')), 1)
        # Description index did not change
        self.assertEqual(len(self.catalog(Description='Bar')), 1)
        self.assertEqual(len(self.catalog(Description='BamBam')), 0)

    def testReindexTitleOnlyUpdatesMetadata(self):
        # Reindexing Title should update metadata
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc, idxs=['Title'])
        brain = self.catalog(getId='doc')[0]
        self.assertEqual(brain.getId, 'doc')
        self.assertEqual(brain.Title, 'Fred')
        self.assertEqual(brain.Description, 'BamBam')

    def testReindexTitleOnlySkipsMetadata(self):
        # Reindexing Title should not update metadata when update_metadata=0
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle('Fred')
        self.folder.doc.setDescription('BamBam')
        self.catalog.reindexObject(self.folder.doc, idxs=['Title'], update_metadata=0)
        brain = self.catalog(getId='doc')[0]
        # Metadata did not change
        self.assertEqual(brain.getId, 'doc')
        self.assertEqual(brain.Title, 'Foo')
        self.assertEqual(brain.Description, 'Bar')

    def testIndexTitleOnly(self):
        # Indexing should only index the Title
        #
        # TODO: This does not work as expected. The object
        # appears to be in the catalog but is not returned
        # by searchResults()!?
        #
        self.catalog.indexObject(self.folder.doc, idxs=['Title'])
        # The document is cataloged
        path = self.catalog._CatalogTool__url(self.folder.doc)
        self.failUnless(path in self.catalog._catalog.paths.values())
        # But it is not returned when searching...
        self.assertEqual(len(self.catalog(getId='doc')), 0)
        self.assertEqual(len(self.catalog(Title='Foo')), 0) # <-- Should be 1
        self.assertEqual(len(self.catalog(Description='Bar')), 0)

    def testIndexIdOnly(self):
        # Indexing should only index the id
        #
        # TODO: Demonstrate that the behavior is independent
        # of index type.
        #
        self.catalog.indexObject(self.folder.doc, idxs=['getId'])
        # The document is cataloged
        path = self.catalog._CatalogTool__url(self.folder.doc)
        self.failUnless(path in self.catalog._catalog.paths.values())
        # But it is not returned when searching...
        self.assertEqual(len(self.catalog(getId='doc')), 0) # <-- Should be 1
        self.assertEqual(len(self.catalog(Title='Foo')), 0)
        self.assertEqual(len(self.catalog(Description='Bar')), 0)

    def testClearFindAndRebuildRemovesBadContent(self):
        # Index the doc for consistency
        self.catalog.indexObject(self.folder.doc)
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)
        # index an object which shouldn't be there
        self.catalog.indexObject(self.portal.portal_skins)
        res = self.catalog.searchResults()
        # Since the introduction of the IIndexableObject interface, we cannot
        # easily get bad content into the catalog anymore
        self.assertResults(res, base_content)
        self.catalog.clearFindAndRebuild()
        # This will add the document added in afterSetup
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)

    def testClearFindAndRebuildAddsMissingContent(self):
        # Index the doc for consistency
        self.catalog.indexObject(self.folder.doc)
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)
        # index an object which shouldn't be there
        self.catalog.unindexObject(self.portal.Members)
        altered_content = base_content[:]
        altered_content.remove('Members')
        res = self.catalog.searchResults()
        self.assertResults(res, altered_content)
        self.catalog.clearFindAndRebuild()
        # This will add the missing item and also the document added
        # in afterSetup
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)

    def testClearFindAndRebuildKeepsModificationDate(self):
        # Index the doc for consistency
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setModificationDate(DateTime(0))
        self.catalog.clearFindAndRebuild()
        self.assertEquals(self.folder.doc.modified(), DateTime(0))
        self.assertEquals(len(self.catalog(modified=DateTime(0))), 1)


class TestCatalogSearching(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.groups = self.portal.portal_groups

        self.portal.acl_users._doAddUser(user2, 'secret', [], [])

        self.folder.invokeFactory('Document', id='doc', text='foo')
        self.folder.invokeFactory('Folder', id='folder2')
        self.folder.folder2.invokeFactory('Document', id='doc2', text='bar')
        self.workflow.doActionFor(self.folder.doc, 'hide', comment='')
        self.workflow.doActionFor(self.folder.folder2, 'hide', comment='')
        self.workflow.doActionFor(self.folder.folder2.doc2, 'hide', comment='')

        # Used for testing AND/OR search functionality below
        self.folder.invokeFactory('Document', id='aaa', text='aaa', title='ccc')
        self.folder.invokeFactory('Document', id='bbb', text='bbb')

        self.setupAuthenticator()

    def addUser2ToGroup(self):
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup(group2, None, [], [])
        group = self.groups.getGroupById(group2)
        self.loginAsPortalOwner() # GRUF 3.52
        group.addMember(user2)
        self.login(default_user) # Back to normal
        return group2

    def testListAllowedRolesAndUsers(self):
        # Should include the group in list of allowed users
        groupname = self.addUser2ToGroup()
        uf = self.portal.acl_users
        self.failUnless(('user:%s' % groupname) in
                self.catalog._listAllowedRolesAndUsers(uf.getUser(user2)))

    def testSearchReturnsDocument(self):
        # Document should be found when owner does a search
        self.assertEqual(self.catalog(SearchableText='aaa')[0].id, 'aaa')

    def testSearchDoesNotReturnDocument(self):
        # Document should not be found when user2 does a search
        self.login(user2)
        self.assertEqual(len(self.catalog(SearchableText='foo')), 0)

    def testSearchReturnsDocumentUsing_DefaultAND(self):
        # Documents should not be found when searching 'aaa bbb' (which should default to AND)
        self.assertEqual(len(self.catalog(SearchableText='aaa bbb')), 0)
        self.assertEqual(len(self.catalog(SearchableText='aaa ccc')), 1)

    def testSearchReturnsDocumentUsing_AND(self):
        # Documents should not be found when owner does a search using AND
        self.assertEqual(len(self.catalog(SearchableText='aaa AND bbb')), 0)
        self.assertEqual(len(self.catalog(SearchableText='aaa AND ccc')), 1)

    def testSearchReturnsDocumentUsing_OR(self):
        # Two documents (aaa, bbb)  should be found when owner does a search using OR
        results = self.catalog(SearchableText='aaa OR bbb')
        self.assertEqual(len(results), 2)

    def testSearchReturnsDocumentWhenPermissionIsTroughLocalRole(self):
        # After adding a group with access rights and containing user2,
        # a search must find the document.
        groupname = self.addUser2ToGroup()
        sharingView = self.folder.unrestrictedTraverse('@@sharing')
        sharingView.update_role_settings([{'id':groupname,
                                           'type':'group',
                                           'roles':['Owner']}])
        self.login(user2)
        self.assertEqual(self.catalog(SearchableText='aaa')[0].id, 'aaa')

    def testSearchRespectsLocalRoleAcquisition(self):
        # After adding a group with access rights and containing user2,
        # a search must find the document in subfolders.
        groupname = self.addUser2ToGroup()
        sharingView = self.folder.unrestrictedTraverse('@@sharing')
        sharingView.update_role_settings([{'id':groupname,
                                           'type':'group',
                                           'roles':['Owner']}])
        self.login(user2)
        # Local Role works in subfolder
        self.assertEqual(self.catalog(SearchableText='bbb')[0].id, 'bbb')

    def testSearchRespectsLocalRoleAcquisitionDisabled(self):
        # After adding a group with access rights and containing user2,
        # a search should not find documents in subfolders which have
        # disabled local role acquisition.
        groupname = self.addUser2ToGroup()
        sharingView = self.folder.unrestrictedTraverse('@@sharing')
        sharingView.update_role_settings([{'id':groupname,
                                           'type':'group',
                                           'roles':['Owner']}])
        # Acquisition off for folder2
        self.folder.folder2.unrestrictedTraverse('@@sharing').update_inherit(False)
        # Everything in subfolder should be invisible
        self.login(user2)
        self.failIf(self.catalog(SearchableText='bar'))


class TestCatalogSorting(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

        self.folder.invokeFactory('Document', id='doc', text='foo')
        self.folder.doc.setTitle('12 Document 25')
        self.folder.invokeFactory('Document', id='doc2', text='foo')
        self.folder.doc2.setTitle('3 Document 4')
        self.folder.invokeFactory('Document', id='doc3', text='foo')
        self.folder.doc3.setTitle('12 Document 4')

        self.folder.invokeFactory('Document', id='doc4', text='bar')
        self.folder.doc4.setTitle('document 12')
        self.folder.invokeFactory('Document', id='doc5', text='bar')
        self.folder.doc5.setTitle('Document 2')
        self.folder.invokeFactory('Document', id='doc6', text='bar')
        self.folder.doc6.setTitle('DOCUMENT 4')
        self.folder.doc.reindexObject()
        self.folder.doc2.reindexObject()
        self.folder.doc3.reindexObject()
        self.folder.doc4.reindexObject()
        self.folder.doc5.reindexObject()
        self.folder.doc6.reindexObject()

    def testSortTitleReturnsProperOrderForNumbers(self):
        # Documents should be returned in proper numeric order
        results = self.catalog(SearchableText='foo', sort_on='sortable_title')
        self.assertEqual(results[0].getId, 'doc2')
        self.assertEqual(results[1].getId, 'doc3')
        self.assertEqual(results[2].getId, 'doc')

    def testSortTitleIgnoresCase(self):
        # Documents should be returned in case insensitive order
        results = self.catalog(SearchableText='bar', sort_on='sortable_title')
        self.assertEqual(results[0].getId, 'doc5')
        self.assertEqual(results[1].getId, 'doc6')
        self.assertEqual(results[2].getId, 'doc4')

    def testSortableTitleOutput(self):
        doc = self.folder.doc
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)

        self.assertEqual(wrapped.sortable_title, u'000012 document 000025')

    def testSortableNonASCIITitles(self):
        #test a utf-8 encoded string gets properly unicode converted
        #sort must ignore accents
        title = 'La Pe\xc3\xb1a'
        doc = self.folder.doc
        doc.setTitle(title)
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.assertEqual(wrapped.sortable_title, 'la pena')

    def testSortableLongNumberPrefix(self):
        title = '1.2.3 foo document'
        doc = self.folder.doc
        doc.setTitle(title)
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.assertEqual(wrapped.sortable_title,
                         u'000001.000002.000003 foo document')
        title = '1.2.3 foo program'
        doc.setTitle(title)
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.assertEqual(wrapped.sortable_title,
                         u'000001.000002.000003 foo program')


class TestFolderCataloging(PloneTestCase.PloneTestCase):
    # Tests for http://dev.plone.org/plone/ticket/2876
    # folder_rename must recatalog.

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Folder', id='foo')
        self.setupAuthenticator()

    def testFolderTitleIsUpdatedOnFolderTitleChange(self):
        # The bug in fact talks about folder_rename
        title = 'Test Folder - Snooze!'
        foo_path = '/'.join(self.folder.foo.getPhysicalPath())
        self.setRequestMethod('POST')
        self.folder.folder_rename(paths=[foo_path], new_ids=['foo'], new_titles=[title])
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.getId, 'foo')

    def testFolderTitleIsUpdatedOnFolderRename(self):
        # The bug in fact talks about folder_rename
        title = 'Test Folder - Snooze!'
        transaction.savepoint(optimistic=True) # make rename work
        foo_path = '/'.join(self.folder.foo.getPhysicalPath())
        self.setRequestMethod('POST')
        self.folder.folder_rename(paths=[foo_path], new_ids=['bar'], new_titles=[title])
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.getId, 'bar')

    def testSetTitleDoesNotUpdateCatalog(self):
        # setTitle() should not update the catalog
        title = 'Test Folder - Snooze!'
        self.failUnless(self.catalog(getId='foo'))
        self.folder.foo.setTitle(title)
        #Title is a TextIndex
        self.failIf(self.catalog(Title='Snooze'))


class TestCatalogOrdering(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', id='doc1', text='foo')
        self.folder.invokeFactory('Document', id='doc2', text='bar')
        self.folder.invokeFactory('Document', id='doc3', text='bloo')
        self.folder.invokeFactory('Document', id='doc4', text='blee')

    def testInitialOrder(self):
        self.failUnlessEqual(self.folder.getObjectPosition('doc1'), 0)
        self.failUnlessEqual(self.folder.getObjectPosition('doc2'), 1)
        self.failUnlessEqual(self.folder.getObjectPosition('doc3'), 2)
        self.failUnlessEqual(self.folder.getObjectPosition('doc4'), 3)

    def testOrderIsUpdatedOnMoveDown(self):
        self.folder.folder_position('down','doc1')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = '/'.join(self.folder.getPhysicalPath()),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc2','doc1','doc3','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveUp(self):
        self.folder.folder_position('up','doc3')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = '/'.join(self.folder.getPhysicalPath()),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','doc3','doc2','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveTop(self):
        self.folder.folder_position('top','doc3')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = '/'.join(self.folder.getPhysicalPath()),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc3','doc1','doc2','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveBottom(self):
        self.folder.folder_position('bottom','doc3')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = '/'.join(self.folder.getPhysicalPath()),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','doc2','doc4','doc3']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectCreation(self):
        self.folder.invokeFactory('Document', id='doc5', text='blam')
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = '/'.join(self.folder.getPhysicalPath()),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','doc2','doc3','doc4','doc5']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectDeletion(self):
        self.folder.manage_delObjects(['doc3',])
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = '/'.join(self.folder.getPhysicalPath()),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','doc2','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectRenaming(self):

        # I don't know why this is failing. manage_renameObjects throws an error
        # that blames permissions or lack of support by the obj. The obj is a
        # Plone Document, and the owner of doc2 is portal_owner. Harumph.

        transaction.savepoint(optimistic=True)

        self.folder.manage_renameObjects(['doc2'], ['buzz'])
        folder_docs = self.catalog(portal_type = 'Document',
                                   path = '/'.join(self.folder.getPhysicalPath()),
                                   sort_on = 'getObjPositionInParent')
        expected = ['doc1','buzz','doc3','doc4']
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testOrderAfterALotOfChanges(self):
        # ['doc1','doc2','doc3','doc4']

        self.folder.folder_position('down','doc1')
        self.folder.folder_position('down','doc1')
        # ['doc2','doc3','doc1','doc4']

        self.folder.folder_position('top','doc3')
        # ['doc3','doc2','doc1','doc4']

        self.folder.invokeFactory('Document', id='doc5', text='blam')
        self.folder.invokeFactory('Document', id='doc6', text='blam')
        self.folder.invokeFactory('Document', id='doc7', text='blam')
        self.folder.invokeFactory('Document', id='doc8', text='blam')
        # ['doc3','doc2','doc1','doc4','doc5','doc6','doc7','doc8',]

        #self.folder.manage_renameObjects('Document', id='doc5', text='blam')

        self.folder.manage_delObjects(['doc3','doc4','doc5','doc7'])
        expected = ['doc2','doc1','doc6','doc8']

        folder_docs = self.catalog(portal_type = 'Document',
                                   path = '/'.join(self.folder.getPhysicalPath()),
                                   sort_on = 'getObjPositionInParent')
        self.failUnlessEqual([b.getId for b in folder_docs], expected)

    def testAllObjectsHaveOrder(self):
        #Make sure that a query with sort_on='getObjPositionInParent'
        #returns the same number of results as one without, make sure
        #the Members folder is in the catalog and has getObjPositionInParent
        all_objs = self.catalog()
        sorted_objs = self.catalog(sort_on='getObjPositionInParent')
        self.failUnlessEqual(len(all_objs), len(sorted_objs))

        members = self.portal.Members
        members_path = '/'.join(members.getPhysicalPath())
        members_query = self.catalog(path=members_path)
        members_sorted = self.catalog(path=members_path, sort_on = 'getObjPositionInParent')
        self.failUnless(len(members_query))
        self.failUnlessEqual(len(members_query),len(members_sorted))


class TestCatalogBugs(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        # Make the catalog tool paste-able
        self._saved = CatalogTool.__replaceable__
        CatalogTool.__replaceable__ = REPLACEABLE

    def afterClear(self):
        CatalogTool.__replaceable__ = self._saved

    def testCanPasteCatalog(self):
        # Should be able to copy/paste a portal_catalog. Triggers
        # manage_afterAdd of portal_catalog thereby exposing another bug :-/
        self.setRoles(['Manager'])
        cb = self.portal.manage_copyObjects(['portal_catalog'])
        self.folder.manage_pasteObjects(cb)
        self.failUnless(hasattr(aq_base(self.folder), 'portal_catalog'))

    def testPastingCatalogPreservesTextIndexes(self):
        # Pasting the catalog should not cause indexes to be removed.
        self.setRoles(['Manager'])
        cb = self.portal.manage_copyObjects(['portal_catalog'])
        self.folder.manage_pasteObjects(cb)
        self.failUnless(hasattr(aq_base(self.folder), 'portal_catalog'))
        cat = self.folder.portal_catalog
        self.failUnless('SearchableText' in cat.indexes())
        # CMF added lexicons should stick around too
        self.failUnless(hasattr(aq_base(cat), 'plaintext_lexicon'))


class TestCatalogUnindexing(PloneTestCase.PloneTestCase):
    # Tests for http://dev.plone.org/plone/ticket/3547
    # Published objects are not unindexed on delete?

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.folder.invokeFactory('Document', id='doc')
        self.setupAuthenticator()

    def testVisibleIsDefault(self):
        state = self.workflow.getInfoFor(self.folder.doc, 'review_state')
        self.assertEqual(state, 'visible')

    def testVisibleCanBeFound(self):
        self.failUnless(self.catalog(getId='doc'))

    def testVisibleIsUnindexed(self):
        self.folder._delObject('doc')
        self.failIf(self.catalog(getId='doc'))

    def testPrivateCanBeFound(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.failUnless(self.catalog(getId='doc'))

    def testPrivateIsUnindexed(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.folder._delObject('doc')
        self.failIf(self.catalog(getId='doc'))

    def testPendingCanBeFound(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.failUnless(self.catalog(getId='doc'))

    def testPendingIsUnindexed(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.folder._delObject('doc')
        self.failIf(self.catalog(getId='doc'))

    def testPublishedCanBeFound(self):
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.failUnless(self.catalog(getId='doc'))

    def testPublishedIsUnindexed(self):
        # Works here!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.folder._delObject('doc')
        self.failIf(self.catalog(getId='doc'))

    def testPublishedIsUnindexedIfOwnerDeletes(self):
        # Works here!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        self.folder._delObject('doc')
        self.failIf(self.catalog(getId='doc'))

    def testPublishedIsUnindexedByFolderDeleteScript(self):
        # Works here too!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        doc_path = '/'.join(self.folder.doc.getPhysicalPath())
        self.app.REQUEST.set('paths', [doc_path])
        # folder_delete requires a non-GET request
        self.setRequestMethod('POST')
        self.folder.folder_delete()
        self.setRequestMethod('GET')
        self.failIf(self.catalog(getId='doc'))

    def testPublishedIsUnindexedWhenDeletingParentFolder(self):
        # Works here too!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        self.folder.aq_parent._delObject(self.folder.getId())
        self.failIf(self.catalog(getId='doc'))


class TestCatalogExpirationFiltering(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', id='doc')

    def nofx(self):
        # Removes effective and expires to make sure we only test
        # the DateRangeIndex.
        self.catalog.delIndex('effective')
        self.catalog.delIndex('expires')

    def assertResults(self, result, expect):
        # Verifies ids of catalog results against expected ids
        lhs = [r.getId for r in result]
        lhs.sort()
        rhs = list(expect)
        rhs.sort()
        self.assertEqual(lhs, rhs)

    def testCeilingPatch(self):
        self.assertEqual(self.folder.doc.expires(), DateTime(2500, 0))

    def testSearchResults(self):
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)

    def testCall(self):
        res = self.catalog()
        self.assertResults(res, base_content)

    def testSearchResultsExpired(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        res = self.catalog.searchResults()
        self.assertResults(res, base_content[:-1])

    def testCallExpired(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        res = self.catalog()
        self.assertResults(res, base_content[:-1])

    def testSearchResultsExpiredWithExpiredDisabled(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        res = self.catalog.searchResults(dict(show_inactive=True))
        self.assertResults(res, base_content)

    def testCallExpiredWithExpiredDisabled(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        res = self.catalog(show_inactive=True)
        self.assertResults(res, base_content)

    def testSearchResultsExpiredWithPermission(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        self.setPermissions([AccessInactivePortalContent])
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)

    def testCallExpiredWithPermission(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        self.setPermissions([AccessInactivePortalContent])
        res = self.catalog()
        self.assertResults(res, base_content)

    def testSearchResultsWithAdditionalExpiryFilter(self):
        # For this test we want the expires and effective indices in place,
        # let's make sure everything still works
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        res = self.catalog.searchResults()
        self.assertResults(res, base_content[:-1])
        # Now make the object expire at some fixed date in the future
        self.folder.doc.setExpirationDate(DateTime()+2)
        self.folder.doc.reindexObject()
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)
        # We should be able to further limit the search using the exipres
        # and efective indices.
        res = self.catalog.searchResults(dict(expires={'query':DateTime()+3,
                                                  'range':'min'}))
        self.assertResults(res, base_content[:-1])

    def testSearchResultsExpiredWithAdditionalExpiryFilter(self):
        # Now make the object expire at some date in the recent past
        self.folder.doc.setExpirationDate(DateTime()-2)
        self.folder.doc.reindexObject()
        res = self.catalog.searchResults()
        self.assertResults(res, base_content[:-1])
        # Even if we explicitly ask for it, we shouldn't get expired content
        res = self.catalog.searchResults(dict(expires={'query':DateTime()-3,
                                                  'range':'min'}))
        self.assertResults(res, base_content[:-1])


def dummyMethod(obj, **kwargs):
    return 'a dummy'

class TestIndexers(PloneTestCase.PloneTestCase):
    """Tests for IIndexer adapters
    """

    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'doc', title='document')
        self.doc = self.folder.doc

    def testSetup(self):
        doc = self.doc
        self.failUnlessEqual(doc.getId(), 'doc')
        self.failUnlessEqual(doc.Title(), 'document')

    def test_is_folderishWithNonFolder(self):
        i = dummy.Item()
        self.failIf(is_folderish(i)())

    def test_is_folderishWithFolder(self):
        f = dummy.Folder('struct_folder')
        self.failUnless(is_folderish(f)())

    def test_is_folderishWithNonStructuralFolder(self):
        f = dummy.NonStructuralFolder('ns_folder')
        self.failIf(is_folderish(f)())

    def test_provided(self):
        from Products.CMFCore.interfaces import IContentish
        from plone.indexer.interfaces import IIndexableObjectWrapper
        from Products.CMFCore.tests.base.dummy import DummyContent

        obj = DummyContent()
        w = IndexableObjectWrapper(obj, self.portal.portal_catalog)

        self.failUnless(IIndexableObjectWrapper.providedBy(w))
        self.failUnless(IContentish.providedBy(w))

    def test_getIcon(self):
        doc = self.doc
        iconname = doc.getIcon(relative_to_portal=1)
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.failUnlessEqual(wrapped.getIcon, iconname)

    def test_uuid(self):
        alsoProvides(self.doc, IAttributeUUID)
        notify(ObjectCreatedEvent(self.doc))

        uuid = IUUID(self.doc, None)
        wrapped = IndexableObjectWrapper(self.doc, self.portal.portal_catalog)
        self.failUnless(wrapped.UID)
        self.failUnless(uuid == wrapped.UID)

class TestObjectProvidedIndexExtender(unittest.TestCase):

    def _index(self, object):
        from Products.CMFPlone.CatalogTool import object_provides
        return object_provides(object)()

    def testNoInterfaces(self):
        class Dummy(object):
            pass
        self.assertEqual(self._index(Dummy()), ())

    def testSimpleInterface(self):
        class IDummy(zope.interface.Interface):
            pass
        class Dummy(object):
            zope.interface.implements(IDummy)
        self.assertEqual(self._index(Dummy()),
            ('Products.CMFPlone.tests.testCatalogTool.IDummy', ))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCatalogSetup))
    suite.addTest(makeSuite(TestCatalogIndexing))
    suite.addTest(makeSuite(TestCatalogSearching))
    suite.addTest(makeSuite(TestFolderCataloging))
    suite.addTest(makeSuite(TestCatalogOrdering))
    suite.addTest(makeSuite(TestCatalogBugs))
    suite.addTest(makeSuite(TestCatalogUnindexing))
    suite.addTest(makeSuite(TestCatalogExpirationFiltering))
    suite.addTest(makeSuite(TestIndexers))
    suite.addTest(makeSuite(TestCatalogSorting))
    suite.addTest(makeSuite(TestObjectProvidedIndexExtender))
    return suite
