from Acquisition import aq_base
from DateTime import DateTime
from functools import partial
from OFS.ObjectManager import REPLACEABLE
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.textfield import RichTextValue
from plone.indexer.wrapper import IndexableObjectWrapper
from plone.uuid.interfaces import IAttributeUUID
from plone.uuid.interfaces import IUUID
from plone.namedfile.file import NamedImage
from Products.CMFCore.indexing import processQueue
from Products.CMFCore.permissions import AccessInactivePortalContent
from Products.CMFPlone.CatalogTool import CatalogTool
from Products.CMFPlone.CatalogTool import is_folderish
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from Products.CMFPlone.tests.utils import folder_position
from z3c.form.interfaces import IFormLayer
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent

import transaction
import unittest
import zope.interface


user2 = "u2"
group2 = "g2"

base_content = [
    "Members",
    "aggregator",
    "aggregator",
    "events",
    "news",
    "plone",
    TEST_USER_ID,
    "doc",
]


class TestCatalogSetup(PloneTestCase):
    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

    def testSearchableTextIsZCTextIndex(self):
        # SearchableText index should be a ZCTextIndex
        itype = self.catalog.Indexes["SearchableText"].__class__.__name__
        self.assertEqual(itype, "ZCTextIndex")

    def testDescriptionIsZCTextIndex(self):
        # Description index should be a ZCTextIndex
        itype = self.catalog.Indexes["Description"].__class__.__name__
        self.assertEqual(itype, "ZCTextIndex")

    def testTitleIsZCTextIndex(self):
        # Title index should be a ZCTextIndex
        itype = self.catalog.Indexes["Title"].__class__.__name__
        self.assertEqual(itype, "ZCTextIndex")

    def testPloneLexiconIsZCTextLexicon(self):
        # Lexicon should be a ZCTextIndex lexicon
        self.assertTrue(hasattr(aq_base(self.catalog), "plone_lexicon"))
        self.assertEqual(self.catalog.plone_lexicon.meta_type, "ZCTextIndex Lexicon")

    def testPathIsExtendedPathIndex(self):
        # path index should be an ExtendedPathIndex
        self.assertEqual(
            self.catalog.Indexes["path"].__class__.__name__, "ExtendedPathIndex"
        )

    def testGetObjPositionInParentIsGopipIndex(self):
        # getObjPositionInParent index should be a FieldIndex
        # also see TestCatalogOrdering below
        self.assertEqual(
            self.catalog.Indexes["getObjPositionInParent"].__class__.__name__,
            "GopipIndex",
        )

    def testGetObjSizeInSchema(self):
        # getObjSize column should be in catalog schema
        self.assertTrue("getObjSize" in self.catalog.schema())

    def testExclude_from_navInSchema(self):
        # exclude_from_nav column should be in catalog schema
        self.assertTrue("exclude_from_nav" in self.catalog.schema())

    def testIs_folderishInSchema(self):
        # is_folderish should be in catalog schema
        self.assertTrue("is_folderish" in self.catalog.schema())

    def testIs_folderishIsBooleanIndex(self):
        # is_folderish should be a BooleanIndex
        self.assertTrue(
            self.catalog.Indexes["is_folderish"].__class__.__name__, "BooleanIndex"
        )

    def testDateIsDateIndex(self):
        # Date should be a DateIndex
        self.assertEqual(self.catalog.Indexes["Date"].__class__.__name__, "DateIndex")

    def testCreatedIsDateIndex(self):
        # created should be a DateIndex
        self.assertEqual(
            self.catalog.Indexes["created"].__class__.__name__, "DateIndex"
        )

    def testEffectiveIsDateIndex(self):
        # effective should be a DateIndex
        self.assertEqual(
            self.catalog.Indexes["effective"].__class__.__name__, "DateIndex"
        )

    def testEndIsDateRecurringIndex(self):
        # end should be a DateRecurringIndex
        self.assertEqual(
            self.catalog.Indexes["end"].__class__.__name__, "DateRecurringIndex"
        )

    def testExpiresIsDateIndex(self):
        # expires should be a DateIndex
        self.assertEqual(
            self.catalog.Indexes["expires"].__class__.__name__, "DateIndex"
        )

    def testModifiedIsDateIndex(self):
        # modified should be a DateIndex
        self.assertEqual(
            self.catalog.Indexes["modified"].__class__.__name__, "DateIndex"
        )

    def testStartIsDateRecurringIndex(self):
        # start should be a DateRecurringIndex
        self.assertEqual(
            self.catalog.Indexes["start"].__class__.__name__, "DateRecurringIndex"
        )

    def testEffectiveRangeIsDateRangeIndex(self):
        # effectiveRange should be a DateRangeIndex
        self.assertEqual(
            self.catalog.Indexes["effectiveRange"].__class__.__name__, "DateRangeIndex"
        )

    def testSortable_TitleIsFieldIndex(self):
        # sortable_title should be a FieldIndex
        self.assertEqual(
            self.catalog.Indexes["sortable_title"].__class__.__name__, "FieldIndex"
        )

    def testExpirationDateInSchema(self):
        # ExpirationDate column should be in catalog schema
        self.assertTrue("ExpirationDate" in self.catalog.schema())

    def testExpiresDateNotInSchema(self):
        # ExpirationDate column should be in catalog schema
        self.assertFalse("ExpiresDate" in self.catalog.schema())

    def testIs_Default_PageIsBooleanIndex(self):
        # is_default_page should be a BooleanIndex
        self.assertEqual(
            self.catalog.Indexes["is_default_page"].__class__.__name__, "BooleanIndex"
        )


class TestCatalogIndexing(PloneTestCase):
    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory("Document", id="doc", title="Foo", description="Bar")
        self.catalog.unindexObject(self.folder.doc)
        processQueue()

    def assertResults(self, result, expect):
        # Verifies ids of catalog results against expected ids
        lhs = [r.getId for r in result]
        lhs.sort()
        rhs = list(expect)
        rhs.sort()
        self.assertEqual(lhs, rhs)

    def testFixture(self):
        self.assertEqual(self.folder.doc.getId(), "doc")
        self.assertEqual(self.folder.doc.Title(), "Foo")
        self.assertEqual(self.folder.doc.Description(), "Bar")
        self.assertEqual(len(self.catalog(getId="doc")), 0)
        self.assertEqual(len(self.catalog(Title="Foo")), 0)
        self.assertEqual(len(self.catalog(Description="Bar")), 0)

    def testIndexObject(self):
        # Object should be indexed
        self.catalog.indexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(getId="doc")), 1)
        self.assertEqual(len(self.catalog(Title="Foo")), 1)
        self.assertEqual(len(self.catalog(Description="Bar")), 1)

    def testReindexObject(self):
        # Object should be indexed
        self.catalog.reindexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(getId="doc")), 1)
        self.assertEqual(len(self.catalog(Title="Foo")), 1)
        self.assertEqual(len(self.catalog(Description="Bar")), 1)

    def testUnindexObject(self):
        # Object should be unindexed
        self.catalog.indexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(getId="doc")), 1)
        self.catalog.unindexObject(self.folder.doc)
        self.assertEqual(len(self.catalog(getId="doc")), 0)

    def testIndexObjectUpdatesMetadata(self):
        # Indexing should update metadata
        self.catalog.indexObject(self.folder.doc)
        brain = self.catalog(getId="doc")[0]
        self.assertEqual(brain.getId, "doc")
        self.assertEqual(brain.Title, "Foo")
        self.assertEqual(brain.Description, "Bar")

    def testReindexObjectUpdatesMetadata(self):
        # Reindexing should update metadata
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle("Fred")
        self.folder.doc.setDescription("BamBam")
        self.catalog.reindexObject(self.folder.doc)
        brain = self.catalog(getId="doc")[0]
        self.assertEqual(brain.getId, "doc")
        self.assertEqual(brain.Title, "Fred")
        self.assertEqual(brain.Description, "BamBam")

    def testReindexObjectSkipsMetadata(self):
        # Reindexing should not update metadata when update_metadata=0
        self.catalog.indexObject(self.folder.doc)
        processQueue()
        self.folder.doc.setTitle("Fred")
        self.folder.doc.setDescription("BamBam")
        self.catalog.reindexObject(self.folder.doc, update_metadata=0)
        brain = self.catalog(getId="doc")[0]
        # Metadata did not change
        self.assertEqual(brain.getId, "doc")
        self.assertEqual(brain.Title, "Foo")
        self.assertEqual(brain.Description, "Bar")

    def testReindexTitleOnly(self):
        # Reindexing should only index the Title
        self.catalog.indexObject(self.folder.doc)
        processQueue()
        self.folder.doc.setTitle("Fred")
        self.folder.doc.setDescription("BamBam")
        self.catalog.reindexObject(self.folder.doc, idxs=["Title"])
        self.assertEqual(len(self.catalog(getId="doc")), 1)
        self.assertEqual(len(self.catalog(Title="Fred")), 1)
        # Description index did not change
        self.assertEqual(len(self.catalog(Description="Bar")), 1)
        self.assertEqual(len(self.catalog(Description="BamBam")), 0)

    def testReindexTitleOnlyUpdatesMetadata(self):
        # Reindexing Title should update metadata
        self.catalog.indexObject(self.folder.doc)
        self.folder.doc.setTitle("Fred")
        self.folder.doc.setDescription("BamBam")
        self.catalog.reindexObject(self.folder.doc, idxs=["Title"])
        brain = self.catalog(getId="doc")[0]
        self.assertEqual(brain.getId, "doc")
        self.assertEqual(brain.Title, "Fred")
        self.assertEqual(brain.Description, "BamBam")

    def testReindexTitleOnlySkipsMetadata(self):
        # Reindexing Title should not update metadata when update_metadata=0
        self.catalog.indexObject(self.folder.doc)
        processQueue()
        self.folder.doc.setTitle("Fred")
        self.folder.doc.setDescription("BamBam")
        self.catalog.reindexObject(self.folder.doc, idxs=["Title"], update_metadata=0)
        brain = self.catalog(getId="doc")[0]
        # Metadata did not change
        self.assertEqual(brain.getId, "doc")
        self.assertEqual(brain.Title, "Foo")
        self.assertEqual(brain.Description, "Bar")

    def testIndexTitleOnly(self):
        # Indexing should only index the Title
        #
        # TODO: This does not work as expected. The object
        # appears to be in the catalog but is not returned
        # by searchResults()!?
        #
        self.catalog.indexObject(self.folder.doc, idxs=["Title"])
        processQueue()
        # The document is cataloged
        path = self.catalog._CatalogTool__url(self.folder.doc)
        self.assertTrue(path in self.catalog._catalog.paths.values())
        # But it is not returned when searching...
        self.assertEqual(len(self.catalog(getId="doc")), 0)
        self.assertEqual(len(self.catalog(Title="Foo")), 0)  # <-- Should be 1
        self.assertEqual(len(self.catalog(Description="Bar")), 0)

    def testIndexIdOnly(self):
        # Indexing should only index the id
        #
        # TODO: Demonstrate that the behavior is independent
        # of index type.
        #
        self.catalog.indexObject(self.folder.doc, idxs=["getId"])
        processQueue()
        # The document is cataloged
        path = self.catalog._CatalogTool__url(self.folder.doc)
        self.assertTrue(path in self.catalog._catalog.paths.values())
        # But it is not returned when searching...
        self.assertEqual(len(self.catalog(getId="doc")), 0)  # <-- Should be 1
        self.assertEqual(len(self.catalog(Title="Foo")), 0)
        self.assertEqual(len(self.catalog(Description="Bar")), 0)

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
        altered_content.remove("Members")
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
        self.folder.doc.modification_date = DateTime(0)
        # FIXME: Index the doc for consistency
        self.catalog.clearFindAndRebuild()
        self.assertEqual(self.folder.doc.modified(), DateTime(0))
        self.assertEqual(len(self.catalog(modified=DateTime(0))), 1)

    def test_acquired_attributes_are_not_indexed(self):
        # create an index for foo:
        # from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
        self.catalog.addIndex("foo", "FieldIndex")

        # create attribute foo on folder and index on both, folder and
        # contained
        self.folder.foo = "FOO"
        self.catalog.clearFindAndRebuild()

        # lets see if we have one result for folder, but nothing for doc:
        brains = self.catalog(foo="FOO")
        self.assertEqual(len(brains), 1)


class TestCatalogSearching(PloneTestCase):
    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.groups = self.portal.portal_groups

        self.portal.acl_users._doAddUser(user2, TEST_USER_PASSWORD, [], [])

        self.folder.invokeFactory("Document", id="doc", text="foo")
        self.folder.invokeFactory("Folder", id="folder2")
        self.folder.folder2.invokeFactory("Document", id="doc2", text="bar")
        self.workflow.doActionFor(self.folder.doc, "hide", comment="")
        self.workflow.doActionFor(self.folder.folder2, "hide", comment="")
        self.workflow.doActionFor(self.folder.folder2.doc2, "hide", comment="")

        # Used for testing AND/OR search functionality below
        self.folder.invokeFactory("Document", id="aaa", text="aaa", title="ccc")
        self.folder.invokeFactory("Document", id="bbb", text="bbb")

        self.setupAuthenticator()

    def addUser2ToGroup(self):
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup(group2, None, [], [])
        group = self.groups.getGroupById(group2)
        self.loginAsPortalOwner()  # GRUF 3.52
        group.addMember(user2)
        self.login(TEST_USER_NAME)  # Back to normal
        return group2

    def testListAllowedRolesAndUsers(self):
        # Should include the group in list of allowed users
        groupname = self.addUser2ToGroup()
        uf = self.portal.acl_users
        user = f"user:{groupname:s}"
        self.assertTrue(
            user in self.catalog._listAllowedRolesAndUsers(uf.getUser(user2))
        )

    def testSearchReturnsDocument(self):
        # Document should be found when owner does a search
        self.assertEqual(self.catalog(SearchableText="aaa")[0].id, "aaa")

    def testSearchDoesNotReturnDocument(self):
        # Document should not be found when user2 does a search
        self.login(user2)
        self.assertEqual(len(self.catalog(SearchableText="foo")), 0)

    def testSearchReturnsDocumentUsing_DefaultAND(self):
        # Documents should not be found when searching 'aaa bbb' (which should
        # default to AND)
        self.assertEqual(len(self.catalog(SearchableText="aaa bbb")), 0)
        self.assertEqual(len(self.catalog(SearchableText="aaa ccc")), 1)

    def testSearchReturnsDocumentUsing_AND(self):
        # Documents should not be found when owner does a search using AND
        self.assertEqual(len(self.catalog(SearchableText="aaa AND bbb")), 0)
        self.assertEqual(len(self.catalog(SearchableText="aaa AND ccc")), 1)

    def testSearchReturnsDocumentUsing_OR(self):
        # Two documents (aaa, bbb)  should be found when owner does a search
        # using OR
        results = self.catalog(SearchableText="aaa OR bbb")
        self.assertEqual(len(results), 2)

    def testSearchIgnoresAccents(self):
        # plip 12110
        self.folder.invokeFactory(
            "Document", id="docwithaccents1", description="Econométrie"
        )
        self.folder.invokeFactory(
            "Document", id="docwithaccents2", description="ECONOMETRIE"
        )
        self.folder.invokeFactory(
            "Document", id="docwithaccents3", description="économétrie"
        )
        self.folder.invokeFactory(
            "Document", id="docwithaccents4", description="ÉCONOMÉTRIE"
        )

        self.assertEqual(len(self.catalog(SearchableText="econometrie")), 4)
        self.assertEqual(len(self.catalog(SearchableText="économétrie")), 4)
        self.assertEqual(len(self.catalog(SearchableText="Econométrie")), 4)
        self.assertEqual(len(self.catalog(SearchableText="ÉCONOMÉTRIE")), 4)

        self.assertEqual(len(self.catalog(SearchableText="econom?trie")), 4)
        self.assertEqual(len(self.catalog(SearchableText="econometr*")), 4)

        # non-regression with eastern language
        # (use plone.i18n ja normalizer test)
        self.folder.invokeFactory(
            "Document", id="docwithjapanchars", description="テストページ"
        )
        self.assertEqual(len(self.catalog(SearchableText="テストページ")), 1)

        # test with language specific char (fr)
        self.folder.invokeFactory(
            "Document", id="docwithfrenchlatinchar", description="œuf"
        )
        self.assertEqual(len(self.catalog(SearchableText="œuf")), 1)
        self.assertEqual(len(self.catalog(SearchableText="oeuf")), 1)
        self.assertEqual(len(self.catalog(SearchableText="Œuf")), 1)
        self.assertEqual(len(self.catalog(SearchableText="OEUF")), 1)
        self.assertEqual(len(self.catalog(SearchableText="uf")), 0)

    def testSearchReturnsDocumentWhenPermissionIsTroughLocalRole(self):
        # After adding a group with access rights and containing user2,
        # a search must find the document.
        groupname = self.addUser2ToGroup()
        sharingView = self.folder.unrestrictedTraverse("@@sharing")
        sharingView.update_role_settings(
            [{"id": groupname, "type": "group", "roles": ["Owner"]}]
        )
        self.login(user2)
        self.assertEqual(self.catalog(SearchableText="aaa")[0].id, "aaa")

    def testSearchRespectsLocalRoleAcquisition(self):
        # After adding a group with access rights and containing user2,
        # a search must find the document in subfolders.
        groupname = self.addUser2ToGroup()
        sharingView = self.folder.unrestrictedTraverse("@@sharing")
        sharingView.update_role_settings(
            [{"id": groupname, "type": "group", "roles": ["Owner"]}]
        )
        self.login(user2)
        # Local Role works in subfolder
        self.assertEqual(self.catalog(SearchableText="bbb")[0].id, "bbb")

    def testSearchRespectsLocalRoleAcquisitionDisabled(self):
        # After adding a group with access rights and containing user2,
        # a search should not find documents in subfolders which have
        # disabled local role acquisition.
        groupname = self.addUser2ToGroup()
        sharingView = self.folder.unrestrictedTraverse("@@sharing")
        sharingView.update_role_settings(
            [{"id": groupname, "type": "group", "roles": ["Owner"]}]
        )
        # Acquisition off for folder2
        self.folder.folder2.unrestrictedTraverse("@@sharing").update_inherit(False)
        # Everything in subfolder should be invisible
        self.login(user2)
        self.assertFalse(self.catalog(SearchableText="bar"))

    def testSearchIgnoreAccents(self):
        """PLIP 12110"""
        self.folder.invokeFactory(
            "Document",
            id="docwithaccents-1",
            text=RichTextValue("Econométrie", "text/html", "text/x-html-safe"),
            title="foo",
        )
        self.folder.invokeFactory(
            "Document",
            id="docwithaccents-2",
            text=RichTextValue("Économétrie", "text/html", "text/x-html-safe"),
        )
        self.folder.invokeFactory(
            "Document",
            id="docwithout-accents",
            text=RichTextValue("ECONOMETRIE", "text/html", "text/x-html-safe"),
        )

        self.assertEqual(len(self.catalog(SearchableText="Économétrie")), 3)
        self.assertEqual(len(self.catalog(SearchableText="Econométrie")), 3)
        self.assertEqual(len(self.catalog(SearchableText="ECONOMETRIE")), 3)

    def testSearchIsProtected(self):
        self.login()
        self.folder.invokeFactory("Document", "sekretz")
        self.logout()
        catalog = self.portal.portal_catalog
        bogus = catalog.search({"portal_type": "Document"})
        real = catalog.portal_catalog.searchResults(portal_type="Document")
        self.assertEqual(len(bogus), len(real))


class TestCatalogSorting(PloneTestCase):
    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

        self.folder.invokeFactory(
            "Document",
            id="doc",
            text=RichTextValue("foo", "text/html", "text/x-html-safe"),
        )
        self.folder.doc.setTitle("12 Document 25")
        self.folder.invokeFactory(
            "Document",
            id="doc2",
            text=RichTextValue("foo", "text/html", "text/x-html-safe"),
        )
        self.folder.doc2.setTitle("3 Document 4")
        self.folder.invokeFactory(
            "Document",
            id="doc3",
            text=RichTextValue("foo", "text/html", "text/x-html-safe"),
        )
        self.folder.doc3.setTitle("12 Document 4")

        self.folder.invokeFactory(
            "Document",
            id="doc4",
            text=RichTextValue("bar", "text/html", "text/x-html-safe"),
        )
        self.folder.doc4.setTitle("document 12")
        self.folder.invokeFactory(
            "Document",
            id="doc5",
            text=RichTextValue("bar", "text/html", "text/x-html-safe"),
        )
        self.folder.doc5.setTitle("Document 2")
        self.folder.invokeFactory(
            "Document",
            id="doc6",
            text=RichTextValue("bar", "text/html", "text/x-html-safe"),
        )
        self.folder.doc6.setTitle("DOCUMENT 4")

        self.folder.invokeFactory("Document", id="doc7")
        self.folder.doc7.setTitle(
            "Long titles used to be truncated, but we changed this, see issue 3690. 0002"
        )

        self.folder.invokeFactory("Document", id="doc8")
        self.folder.doc8.setTitle(
            "Long titles used to be truncated, but we changed this, see issue 3690. 0001"
        )

        self.folder.doc.reindexObject()
        self.folder.doc2.reindexObject()
        self.folder.doc3.reindexObject()
        self.folder.doc4.reindexObject()
        self.folder.doc5.reindexObject()
        self.folder.doc6.reindexObject()
        self.folder.doc7.reindexObject()
        self.folder.doc8.reindexObject()

    def testSortMultipleColumns(self):
        path = "/".join(self.folder.getPhysicalPath())
        query = partial(self.catalog, path=path)
        brains = query(sort_on=["portal_type", "sortable_title"])
        self.assertListEqual(
            [brain.getPath() for brain in brains],
            [
                "/plone/Members/test_user_1_/doc2",
                "/plone/Members/test_user_1_/doc3",
                "/plone/Members/test_user_1_/doc",
                "/plone/Members/test_user_1_/doc5",
                "/plone/Members/test_user_1_/doc6",
                "/plone/Members/test_user_1_/doc4",
                "/plone/Members/test_user_1_/doc8",
                "/plone/Members/test_user_1_/doc7",
                "/plone/Members/test_user_1_",
            ],
        )
        brains = query(sort_on=["portal_type", "getId"])
        self.assertListEqual(
            [brain.getPath() for brain in brains],
            [
                "/plone/Members/test_user_1_/doc",
                "/plone/Members/test_user_1_/doc2",
                "/plone/Members/test_user_1_/doc3",
                "/plone/Members/test_user_1_/doc4",
                "/plone/Members/test_user_1_/doc5",
                "/plone/Members/test_user_1_/doc6",
                "/plone/Members/test_user_1_/doc7",
                "/plone/Members/test_user_1_/doc8",
                "/plone/Members/test_user_1_",
            ],
        )

    def testUnknownSortOnIsIgnored(self):
        # You should not get a CatalogError when an invalid sort_on is passed.
        # I get crazy sort_ons like '194' or 'null'.
        self.assertTrue(len(self.catalog(SearchableText="foo", sort_on="194")) > 0)
        self.assertTrue(len(self.catalog(SearchableText="foo", sort_on="null")) > 0)
        self.assertTrue(
            len(self.catalog(SearchableText="foo", sort_on="relevance")) > 0
        )

    def testSortTitleReturnsProperOrderForNumbers(self):
        # Documents should be returned in proper numeric order
        results = self.catalog(SearchableText="foo", sort_on="sortable_title")
        self.assertEqual(results[0].getId, "doc2")
        self.assertEqual(results[1].getId, "doc3")
        self.assertEqual(results[2].getId, "doc")

    def testSortTitleIgnoresCase(self):
        # Documents should be returned in case insensitive order
        results = self.catalog(SearchableText="bar", sort_on="sortable_title")
        self.assertEqual(results[0].getId, "doc5")
        self.assertEqual(results[1].getId, "doc6")
        self.assertEqual(results[2].getId, "doc4")

    def testSortableTitleOutput(self):
        doc = self.folder.doc
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)

        self.assertEqual(wrapped.sortable_title, "0012 document 0025")

    def testSortableTitleInLongTitles(self):
        doc = self.folder.doc7
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)

        self.assertEqual(
            wrapped.sortable_title,
            "long titles used to be truncated, but we changed this, see issue 3690. 0002",
        )

    def testSortableNonASCIITitles(self):
        # test a utf-8 encoded string gets properly unicode converted
        # sort must ignore accents
        title = b"La Pe\xc3\xb1a"
        doc = self.folder.doc
        doc.title = title.decode("utf-8")
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.assertEqual(wrapped.sortable_title, "la pena")

    def testSortableDate(self):
        title = "2012-06-01 foo document"
        doc = self.folder.doc
        doc.setTitle(title)
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.assertEqual(wrapped.sortable_title, "2012-0006-0001 foo document")

    def testSortableLongNumberPrefix(self):
        title = "1.2.3 foo document"
        doc = self.folder.doc
        doc.setTitle(title)
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.assertEqual(wrapped.sortable_title, "0001.0002.0003 foo document")
        title = "1.2.3 foo program"
        doc.setTitle(title)
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.assertEqual(wrapped.sortable_title, "0001.0002.0003 foo program")

    def testSortableLongCommonPrefix(self):
        title = (
            "some documents have too long a name and only differ at "
            "the very end - like 1.jpeg"
        )
        doc = self.folder.doc
        doc.setTitle(title)
        wrapped = IndexableObjectWrapper(doc, self.portal.portal_catalog)
        self.assertEqual(
            wrapped.sortable_title,
            "some documents have too long a name and only differ at the very end - like 0001.jpeg",
        )


class TestFolderCataloging(PloneTestCase):
    # Tests for http://dev.plone.org/plone/ticket/2876
    # folder_rename must recatalog.

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory("Folder", id="foo")
        self.setupAuthenticator()

        # z3c.form needs IFormLayer provided by request
        alsoProvides(self.folder.REQUEST, IFormLayer)

    def testFolderTitleIsUpdatedOnFolderTitleChange(self):
        title = "Test Folder - Snooze!"

        self.folder.REQUEST.form = {
            "form.widgets.new_id": "foo",
            "form.widgets.new_title": title,
        }
        form = self.folder.restrictedTraverse("@@folder_rename")
        form.update()

        self.loginAsPortalOwner()
        button = form.buttons["Rename"]
        form.handlers.getHandler(button)(form, button)

        results = self.catalog(Title="Snooze")
        self.assertTrue(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.getId, "foo")

    def testFolderTitleIsUpdatedOnFolderRename(self):
        title = "Test Folder - Snooze!"

        self.folder.REQUEST.form = {
            "form.widgets.new_id": "bar",
            "form.widgets.new_title": title,
        }
        form = self.folder.restrictedTraverse("@@folder_rename")
        form.update()

        self.loginAsPortalOwner()
        button = form.buttons["Rename"]
        form.handlers.getHandler(button)(form, button)

        results = self.catalog(Title="Snooze")
        self.assertTrue(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.getId, "bar")

    def testSetTitleDoesNotUpdateCatalog(self):
        # setTitle() should not update the catalog
        title = "Test Folder - Snooze!"
        self.assertTrue(self.catalog(getId="foo"))
        self.folder.foo.setTitle(title)
        # Title is a TextIndex
        self.assertFalse(self.catalog(Title="Snooze"))


class TestCatalogOrdering(PloneTestCase):
    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory("Document", id="doc1", text="foo", title="First")
        self.folder.invokeFactory("Document", id="doc2", text="bar", title="Second")
        self.folder.invokeFactory("Document", id="doc3", text="bloo", title="Third")
        self.folder.invokeFactory("Document", id="doc4", text="blee", title="Fourth")

    def testInitialOrder(self):
        self.assertEqual(self.folder.getObjectPosition("doc1"), 0)
        self.assertEqual(self.folder.getObjectPosition("doc2"), 1)
        self.assertEqual(self.folder.getObjectPosition("doc3"), 2)
        self.assertEqual(self.folder.getObjectPosition("doc4"), 3)

    def testOrderIsUnchangedOnDefaultFolderPosition(self):
        # Calling the folder_position script with no arguments should
        # give no complaints and have no effect.
        folder_position(self.folder)
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc1", "doc2", "doc3", "doc4"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveDown(self):
        folder_position(self.folder, "down", "doc1")
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc2", "doc1", "doc3", "doc4"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveUp(self):
        folder_position(self.folder, "up", "doc3")
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc1", "doc3", "doc2", "doc4"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveTop(self):
        folder_position(self.folder, "top", "doc3")
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc3", "doc1", "doc2", "doc4"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnMoveBottom(self):
        folder_position(self.folder, "bottom", "doc3")
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc1", "doc2", "doc4", "doc3"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnSort(self):
        folder_position(self.folder, position="ordered", id="Title")
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc1", "doc4", "doc2", "doc3"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnReverse(self):
        folder_position(self.folder, position="ordered", id="Title", reverse=True)
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc3", "doc2", "doc4", "doc1"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsUpdatedOnSimpleReverse(self):
        folder_position(self.folder, position="ordered", reverse=True)
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc4", "doc3", "doc2", "doc1"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectCreation(self):
        self.folder.invokeFactory("Document", id="doc5", text="blam")
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc1", "doc2", "doc3", "doc4", "doc5"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectDeletion(self):
        self.folder.manage_delObjects(
            [
                "doc3",
            ]
        )
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc1", "doc2", "doc4"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderIsFineWithObjectRenaming(self):
        # I don't know why this is failing. manage_renameObjects throws an
        # error that blames permissions or lack of support by the obj. The
        # obj is a # Plone Document, and the owner of doc2 is portal_owner.
        # Harumph.

        transaction.savepoint(optimistic=True)

        self.folder.manage_renameObjects(["doc2"], ["buzz"])
        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        expected = ["doc1", "buzz", "doc3", "doc4"]
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testOrderAfterALotOfChanges(self):
        # ['doc1','doc2','doc3','doc4']

        folder_position(self.folder, "down", "doc1")
        folder_position(self.folder, "down", "doc1")
        # ['doc2','doc3','doc1','doc4']

        folder_position(self.folder, "top", "doc3")
        # ['doc3','doc2','doc1','doc4']

        self.folder.invokeFactory("Document", id="doc5", text="blam")
        self.folder.invokeFactory("Document", id="doc6", text="blam")
        self.folder.invokeFactory("Document", id="doc7", text="blam")
        self.folder.invokeFactory("Document", id="doc8", text="blam")
        # ['doc3','doc2','doc1','doc4','doc5','doc6','doc7','doc8',]

        # self.folder.manage_renameObjects('Document', id='doc5', text='blam')

        self.folder.manage_delObjects(["doc3", "doc4", "doc5", "doc7"])
        expected = ["doc2", "doc1", "doc6", "doc8"]

        folder_docs = self.catalog(
            portal_type="Document",
            path="/".join(self.folder.getPhysicalPath()),
            sort_on="getObjPositionInParent",
        )
        self.assertEqual([b.getId for b in folder_docs], expected)

    def testAllObjectsHaveOrder(self):
        # Make sure that a query with sort_on='getObjPositionInParent'
        # returns the same number of results as one without, make sure
        # the Members folder is in the catalog and has getObjPositionInParent
        all_objs = self.catalog()
        sorted_objs = self.catalog(sort_on="getObjPositionInParent")
        self.assertEqual(len(all_objs), len(sorted_objs))

        members = self.portal.Members
        members_path = "/".join(members.getPhysicalPath())
        members_query = self.catalog(path=members_path)
        members_sorted = self.catalog(
            path=members_path,
            sort_on="getObjPositionInParent",
        )
        self.assertTrue(len(members_query))
        self.assertEqual(len(members_query), len(members_sorted))

    def testGopipIndexer(self):
        from Products.CMFPlone.CatalogTool import getObjPositionInParent

        get_pos = getObjPositionInParent.callable
        self.assertEqual(get_pos(self.folder.doc1), 0)
        self.assertEqual(get_pos(self.folder.doc4), 3)


class TestCatalogBugs(PloneTestCase):
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
        self.setRoles(["Manager"])
        cb = self.portal.manage_copyObjects(["portal_catalog"])
        self.folder.manage_pasteObjects(cb)
        self.assertTrue(hasattr(aq_base(self.folder), "portal_catalog"))

    def testPastingCatalogPreservesTextIndexes(self):
        # Pasting the catalog should not cause indexes to be removed.
        self.setRoles(["Manager"])
        cb = self.portal.manage_copyObjects(["portal_catalog"])
        self.folder.manage_pasteObjects(cb)
        self.assertTrue(hasattr(aq_base(self.folder), "portal_catalog"))
        cat = self.folder.portal_catalog
        self.assertTrue("SearchableText" in cat.indexes())
        # CMF added lexicons should stick around too
        self.assertTrue(hasattr(aq_base(cat), "plaintext_lexicon"))


class TestCatalogUnindexing(PloneTestCase):
    # Tests for http://dev.plone.org/plone/ticket/3547
    # Published objects are not unindexed on delete?

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.folder.invokeFactory("Document", id="doc")
        self.setupAuthenticator()

    def testVisibleIsDefault(self):
        state = self.workflow.getInfoFor(self.folder.doc, "review_state")
        self.assertEqual(state, "visible")

    def testVisibleCanBeFound(self):
        self.assertTrue(self.catalog(getId="doc"))

    def testVisibleIsUnindexed(self):
        self.folder._delObject("doc")
        self.assertFalse(self.catalog(getId="doc"))

    def testPrivateCanBeFound(self):
        self.workflow.doActionFor(self.folder.doc, "hide")
        self.assertTrue(self.catalog(getId="doc"))

    def testPrivateIsUnindexed(self):
        self.workflow.doActionFor(self.folder.doc, "hide")
        self.folder._delObject("doc")
        self.assertFalse(self.catalog(getId="doc"))

    def testPendingCanBeFound(self):
        self.workflow.doActionFor(self.folder.doc, "submit")
        self.assertTrue(self.catalog(getId="doc"))

    def testPendingIsUnindexed(self):
        self.workflow.doActionFor(self.folder.doc, "submit")
        self.folder._delObject("doc")
        self.assertFalse(self.catalog(getId="doc"))

    def testPublishedCanBeFound(self):
        self.setRoles(["Manager"])
        self.workflow.doActionFor(self.folder.doc, "publish")
        self.assertTrue(self.catalog(getId="doc"))

    def testPublishedIsUnindexed(self):
        self.setRoles(["Manager"])
        self.workflow.doActionFor(self.folder.doc, "publish")
        self.folder._delObject("doc")
        self.assertFalse(self.catalog(getId="doc"))

    def testPublishedIsUnindexedIfOwnerDeletes(self):
        self.setRoles(["Manager"])
        self.workflow.doActionFor(self.folder.doc, "publish")
        self.setRoles(["Member"])
        self.folder._delObject("doc")
        self.assertFalse(self.catalog(getId="doc"))

    def testPublishedIsUnindexedByFolderDeleteScript(self):
        doc = self.folder.doc
        self.setRoles(["Manager"])
        self.workflow.doActionFor(doc, "publish")
        self.setRoles(["Member"])
        alsoProvides(doc.REQUEST, IFormLayer)
        doc.restrictedTraverse("@@object_delete")()
        self.assertFalse(self.catalog(getId="doc"))

    def testPublishedIsUnindexedWhenDeletingParentFolder(self):
        # Works here too!
        self.setRoles(["Manager"])
        self.workflow.doActionFor(self.folder.doc, "publish")
        self.setRoles(["Member"])
        self.folder.aq_parent._delObject(self.folder.getId())
        self.assertFalse(self.catalog(getId="doc"))


class TestCatalogExpirationFiltering(PloneTestCase):
    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory("Document", id="doc")

        # Create unprivileged user
        self.portal.acl_users._doAddUser(user2, TEST_USER_PASSWORD, ["Member"], [])

    def nofx(self):
        # Removes effective and expires to make sure we only test
        # the DateRangeIndex.
        self.catalog.delIndex("effective")
        self.catalog.delIndex("expires")

    def assertResults(self, result, expect):
        # Verifies ids of catalog results against expected ids
        lhs = [r.getId for r in result]
        lhs.sort()
        rhs = list(expect)
        rhs.sort()
        self.assertEqual(lhs, rhs)

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
        self.login(user2)
        res = self.catalog.searchResults()
        self.assertResults(res, base_content[:-1])

    def testCallExpired(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        self.login(user2)
        res = self.catalog()
        self.assertResults(res, base_content[:-1])

    def testSearchResultsExpiredWithExpiredDisabled(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        self.login(user2)
        res = self.catalog.searchResults(dict(show_inactive=True))
        self.assertResults(res, base_content)

    def testCallExpiredWithExpiredDisabled(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        self.login(user2)
        res = self.catalog(show_inactive=True)
        self.assertResults(res, base_content)

    def testSearchResultsExpiredWithPermission(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()
        self.login(user2)
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

    def testPathWithPrivateMidLevel(self):
        # This test was added to test issue where allow_inactive-check raised
        # Unauthorized-exception with the search conditions of this test.

        # Be anonymous to enable allow_inactive -check
        self.logout()

        # Check that search shows both self.folder and self.folder.doc
        path = "/".join(self.folder.aq_parent.getPhysicalPath())
        results = [b.getPath() for b in self.catalog(path=path)]
        self.assertIn("/".join(self.folder.getPhysicalPath()), results)
        self.assertIn("/".join(self.folder.doc.getPhysicalPath()), results)

        # Hide self.folder from anonymous, but leave self.folder.doc visible
        self.login(TEST_USER_NAME)
        self.portal.portal_workflow.doActionFor(self.folder, "hide")
        self.logout()

        # Check that self.folder.doc is still visible while self.folder is not
        results = [b.getPath() for b in self.catalog(path=path)]
        self.assertNotIn("/".join(self.folder.getPhysicalPath()), results)
        self.assertIn("/".join(self.folder.doc.getPhysicalPath()), results)

        # Check that direct search for self.folder.doc can be made
        path = "/".join(self.folder.doc.getPhysicalPath())
        results = [b.getPath() for b in self.catalog(path=path)]
        self.assertIn("/".join(self.folder.doc.getPhysicalPath()), results)

    def testUnauthorizedIsNotRaisedOnShowInactive(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        wf_tool = self.portal.portal_workflow
        self.portal.invokeFactory("Folder", id="folder1")
        folder = self.portal["folder1"]
        wf_tool.doActionFor(folder, "publish", comment="")
        folder.reindexObject()

        folder.invokeFactory("Folder", id="folder2")
        folder2 = folder["folder2"]
        wf_tool.doActionFor(folder2, "hide", comment="")
        folder2.reindexObject()

        folder2.invokeFactory("Document", id="doc1")
        doc = folder2["doc1"]
        wf_tool.doActionFor(doc, "publish", comment="")
        doc.reindexObject()

        folder2.invokeFactory("Document", id="doc2")
        doc2 = folder2["doc2"]
        wf_tool.doActionFor(doc2, "hide", comment="")
        doc2.reindexObject()

        self.logout()
        path = "/" + folder2.absolute_url(1)
        results = self.catalog.searchResults(path=path)
        self.assertEqual(results[0].getPath(), "/plone/folder1/folder2/doc1")
        self.assertEqual(len(results), 1)

    def testExpiredWithPermissionOnSubpath(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()

        # Login as unprivileged user
        self.login(user2)

        self.folder.manage_role("Member", [AccessInactivePortalContent])

        expected_result = ["doc", "test_user_1_"]

        query = {"path": "/".join(self.folder.getPhysicalPath())}
        res = self.catalog.searchResults(**query)
        self.assertResults(res, expected_result)
        res = self.catalog(**query)
        self.assertResults(res, expected_result)

        query = {"path": {"query": "/".join(self.folder.getPhysicalPath())}}
        res = self.catalog.searchResults(**query)
        self.assertResults(res, expected_result)
        res = self.catalog(**query)
        self.assertResults(res, expected_result)

        query = {
            "path": {
                "query": [
                    "/".join(self.folder.getPhysicalPath()),
                    "/".join(self.folder.doc.getPhysicalPath()),
                ]
            }
        }
        res = self.catalog.searchResults(**query)
        self.assertResults(res, expected_result)
        res = self.catalog(**query)
        self.assertResults(res, expected_result)

    def testExpiredWithoutPermissionOnSubpath(self):
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()

        # Login as unprivileged user
        self.login(user2)

        # Inactive content isn't shown without the required permission.
        expected_result = ["test_user_1_"]

        query = {"path": "/".join(self.folder.getPhysicalPath())}
        res = self.catalog.searchResults(**query)
        self.assertResults(res, expected_result)
        res = self.catalog(**query)
        self.assertResults(res, expected_result)

        query = {"path": {"query": "/".join(self.folder.getPhysicalPath())}}
        res = self.catalog.searchResults(**query)
        self.assertResults(res, expected_result)
        res = self.catalog(**query)
        self.assertResults(res, expected_result)

        query = {
            "path": {
                "query": [
                    "/".join(self.folder.getPhysicalPath()),
                    "/".join(self.folder.doc.getPhysicalPath()),
                ]
            }
        }
        res = self.catalog.searchResults(**query)
        self.assertResults(res, expected_result)
        res = self.catalog(**query)
        self.assertResults(res, expected_result)

    def testExpiredWithSameNameAsSite(self):
        # Create an expired folder with the same name as the site
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Folder", id=self.portal.id)

        # Add the AccessInactivePortalContent permission in the plone folder
        # The user should NOT have this permission in self.folder
        self.portal.plone.manage_role("Member", [AccessInactivePortalContent])

        # Expire a document
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        self.nofx()

        # Inactive content isn't shown without the required permission.
        expected_result = [content for content in base_content if content != "doc"] + [
            "plone"
        ]

        # Login as unprivileged user
        self.login(user2)

        # Path is the site's one
        query = {"path": "/".join(self.portal.getPhysicalPath())}
        res = self.catalog.searchResults(**query)
        self.assertResults(res, expected_result)
        res = self.catalog(**query)
        self.assertResults(res, expected_result)

    def testSearchResultsWithAdditionalExpiryFilter(self):
        # For this test we want the expires and effective indices in place,
        # let's make sure everything still works
        self.folder.doc.setExpirationDate(DateTime(2000, 12, 31))
        self.folder.doc.reindexObject()
        res = self.catalog.searchResults()
        self.assertResults(res, base_content[:-1])
        # Now make the object expire at some fixed date in the future
        self.folder.doc.setExpirationDate(DateTime() + 2)
        self.folder.doc.reindexObject()
        res = self.catalog.searchResults()
        self.assertResults(res, base_content)
        # We should be able to further limit the search using the expires
        # and effective indices.
        res = self.catalog.searchResults(
            {
                "expires": {"query": DateTime() + 3, "range": "min"},
            }
        )

        self.assertResults(res, base_content[:-1])

    def testSearchResultsExpiredWithAdditionalExpiryFilter(self):
        # Now make the object expire at some date in the recent past
        self.folder.doc.setExpirationDate(DateTime() - 2)
        self.folder.doc.reindexObject()
        res = self.catalog.searchResults()
        self.assertResults(res, base_content[:-1])
        # Even if we explicitly ask for it, we shouldn't get expired content
        res = self.catalog.searchResults(
            {
                "expires": {"query": DateTime() - 3, "range": "min"},
            }
        )
        self.assertResults(res, base_content[:-1])


def dummyMethod(obj, **kwargs):
    return "a dummy"


class TestIndexers(PloneTestCase):
    """Tests for IIndexer adapters"""

    def afterSetUp(self):
        self.folder.invokeFactory("Document", "doc", title="document")
        self.doc = self.folder.doc

    def testSetup(self):
        doc = self.doc
        self.assertEqual(doc.getId(), "doc")
        self.assertEqual(doc.Title(), "document")

    def test_is_folderishWithNonFolder(self):
        i = dummy.Item()
        self.assertFalse(is_folderish(i)())

    def test_is_folderishWithFolder(self):
        f = dummy.Folder("struct_folder")
        self.assertTrue(is_folderish(f)())

    def test_is_folderishWithNonStructuralFolder(self):
        f = dummy.NonStructuralFolder("ns_folder")
        self.assertFalse(is_folderish(f)())

    def test_provided(self):
        from plone.indexer.interfaces import IIndexableObjectWrapper
        from Products.CMFCore.interfaces import IContentish
        from Products.CMFCore.tests.base.dummy import DummyContent

        obj = DummyContent()
        w = IndexableObjectWrapper(obj, self.portal.portal_catalog)

        self.assertTrue(IIndexableObjectWrapper.providedBy(w))
        self.assertTrue(IContentish.providedBy(w))

    def test_getObjSize_KB(self):
        from Products.CMFPlone.CatalogTool import getObjSize

        get_size = getObjSize.callable
        self.doc.text = RichTextValue("a" * 1000)
        self.doc.reindexObject()
        self.assertEqual(get_size(self.doc), "1 KB")

    def test_getObjSize_MB(self):
        from Products.CMFPlone.CatalogTool import getObjSize

        get_size = getObjSize.callable
        self.doc.text = RichTextValue("a" * 6000000)
        self.doc.reindexObject()
        self.assertEqual(get_size(self.doc), "5.7 MB")

    def test_uuid(self):
        alsoProvides(self.doc, IAttributeUUID)
        notify(ObjectCreatedEvent(self.doc))

        uuid = IUUID(self.doc, None)
        wrapped = IndexableObjectWrapper(self.doc, self.portal.portal_catalog)
        self.assertTrue(wrapped.UID)
        self.assertTrue(uuid == wrapped.UID)

    def test_getIcon(self):
        from Products.CMFPlone.CatalogTool import getIcon

        get_icon = getIcon.callable
        self.assertFalse(get_icon(self.folder))
        # Create an item inside the test folder
        self.folder.invokeFactory("Image", "image", title="Image")
        # Do not get the "image" content item
        self.assertFalse(get_icon(self.folder))
        # Return False if item doesn't have an image
        self.assertFalse(get_icon(self.folder.image))
        self.folder.image.image=NamedImage(dummy.Image())
        # Item has a proper image, return True
        self.assertTrue(get_icon(self.folder.image))


class TestObjectProvidedIndexExtender(unittest.TestCase):
    def _index(self, object):
        from Products.CMFPlone.CatalogTool import object_provides

        return object_provides(object)()

    def testNoInterfaces(self):
        class Dummy:
            pass

        self.assertEqual(self._index(Dummy()), ())

    def testSimpleInterface(self):
        class IDummy(zope.interface.Interface):
            pass

        @zope.interface.implementer(IDummy)
        class Dummy:
            pass

        self.assertEqual(
            self._index(Dummy()), ("Products.CMFPlone.tests.testCatalogTool.IDummy",)
        )
