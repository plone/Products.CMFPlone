#
# CatalogTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base
from Globals import REPLACEABLE

portal_name = PloneTestCase.portal_name

user1  = PloneTestCase.default_user
user2  = 'u2'
group2 = 'g2'


class TestCatalogTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

    def testPloneLexiconIsZCTextLexicon(self):
        # Lexicon should be a ZCTextIndex lexicon
        self.failUnless(hasattr(aq_base(self.catalog), 'plone_lexicon'))
        self.assertEqual(self.catalog.plone_lexicon.meta_type, 'ZCTextIndex Lexicon')

    def testSearchableTextIsZCTextIndex(self):
        # SearchableText index should be a ZCTextIndex
        self.assertEqual(self.catalog.Indexes['SearchableText'].__class__.__name__,
                         'ZCTextIndex')

    def testDescriptionIsTextIndex(self):
        # Description index should be a TextIndex
        self.assertEqual(self.catalog.Indexes['Description'].__class__.__name__,
                         'TextIndex')

    def testTitleIsTextIndex(self):
        # Title index should be a TextIndex
        self.assertEqual(self.catalog.Indexes['Title'].__class__.__name__,
                         'TextIndex')


class TestCatalogSearch(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.groups = self.portal.portal_groups

        self.portal.acl_users._doAddUser(user2, 'secret', [], [], [])

        self.folder.invokeFactory('Document', id='doc', text='foo')
        self.workflow.doActionFor(self.folder.doc, 'hide', comment='')

    def addUser2ToGroup(self):
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup(group2, None, [], [])
        group = self.groups.getGroupById(group2)
        group.addMember(user2)
        prefix = self.portal.acl_users.getGroupPrefix()
        return '%s%s' % (prefix, group2)

    def testListAllowedRolesAndUsers(self):
        # Should include the group in list of allowed users
        groupname = self.addUser2ToGroup()
        uf = self.portal.acl_users
        self.failUnless(('user:%s' % groupname) in
                self.catalog._listAllowedRolesAndUsers(uf.getUser(user2)))

    def testSearchReturnsDocument(self):
        # Document should be found when owner does a search
        self.assertEqual(self.catalog(SearchableText='foo')[0].id, 'doc')

    def testSearchDoesNotReturnDocument(self):
        # Document should not be found when user2 does a search
        self.login(user2)
        self.assertEqual(len(self.catalog(SearchableText='foo')), 0)

    def testSearchReturnsDocumentWhenPermissionIsTroughLocalRole(self):
        # After adding a group with access rights and containing user2,
        # a search must find the document.
        groupname = self.addUser2ToGroup()
        self.folder.folder_localrole_edit('add', [groupname], 'Owner')
        self.login(user2)
        self.assertEqual(self.catalog(SearchableText='foo')[0].id, 'doc')


class TestFolderCataloging(PloneTestCase.PloneTestCase):
    # Tests for http://plone.org/collector/2876
    # folder_edit must recatalog. folder_rename must recatalog.

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Folder', id='foo')

    def testFolderTitleIsUpdatedOnEdit(self):
        # Test for catalog that searches to ensure folder titles are 
        # updated in the catalog. 
        title = 'Test Folder - Snooze!'
        self.folder.foo.folder_edit(title, '')
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'foo')

    def testFolderTitleIsUpdatedOnRename(self):
        # Test for catalog that searches to ensure folder titles are 
        # updated in the catalog. 
        title = 'Test Folder - Snooze!'
        get_transaction().commit(1) # make rename work
        self.folder.foo.folder_edit(title, '', id='bar')
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'bar')

    def testFolderTitleIsUpdatedOnFolderTitleChange(self):
        # The bug in fact talks about folder_rename
        title = 'Test Folder - Snooze!'
        self.folder.folder_rename(ids=['foo'], new_ids=['foo'], new_titles=[title])
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'foo')

    def testFolderTitleIsUpdatedOnFolderRename(self):
        # The bug in fact talks about folder_rename
        title = 'Test Folder - Snooze!'
        get_transaction().commit(1) # make rename work
        self.folder.folder_rename(ids=['foo'], new_ids=['bar'], new_titles=[title])
        results = self.catalog(Title='Snooze')
        self.failUnless(results)
        for result in results:
            self.assertEqual(result.Title, title)
            self.assertEqual(result.id, 'bar')

    def testSetTitleDoesNotUpdateCatalog(self):
        # setTitle() should not update the catalog
        title = 'Test Folder - Snooze!'
        self.failUnless(self.catalog(id='foo'))
        self.folder.foo.setTitle(title)
        self.failIf(self.catalog(Title='Snooze'))


class TestCatalogBugs(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

    def testCanPastePortalIfLexiconExists(self):
        # Should be able to copy/paste a portal containing
        # a catalog tool. Triggers manage_afterAdd of portal_catalog
        # thereby exposing a bug which is now going to be fixed.
        self.loginPortalOwner()
        cb = self.app.manage_copyObjects([portal_name])
        self.app.manage_pasteObjects(cb)
        self.failUnless(hasattr(self.app, 'copy_of_'+portal_name))

    def testCanPasteCatalog(self):
        # Should be able to copy/paste a portal_catalog. Triggers
        # manage_afterAdd of portal_catalog thereby exposing another bug :-/
        self.setRoles(['Manager'])
        self.catalog.__replaceable__ = REPLACEABLE
        cb = self.portal.manage_copyObjects(['portal_catalog'])
        self.folder.manage_pasteObjects(cb)
        self.failUnless(hasattr(aq_base(self.folder), 'portal_catalog'))

    def testCanRenamePortalIfLexiconExists(self):
        # Should be able to rename a Plone portal
        # This test is to demonstrate that http://plone.org/collector/1745
        # is fixed and can be closed.
        self.loginPortalOwner()
        self.app.manage_renameObjects([portal_name], ['foo'])
        self.failUnless(hasattr(self.app, 'foo'))


class TestCatalogUnindexing(PloneTestCase.PloneTestCase):
    # Tests for http://plone.org/collector/3547
    # Published objects are not unindexed on delete?

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.folder.invokeFactory('Document', id='doc')

    def testVisibleIsDefault(self):
        state = self.workflow.getInfoFor(self.folder.doc, 'review_state')
        self.assertEqual(state, 'visible')

    def testVisibleCanBeFound(self):
        self.failUnless(self.catalog(id='doc'))

    def testVisibleIsUnindexed(self):
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPrivateCanBeFound(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.failUnless(self.catalog(id='doc'))

    def testPrivateIsUnindexed(self):
        self.workflow.doActionFor(self.folder.doc, 'hide')
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPendingCanBeFound(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.failUnless(self.catalog(id='doc'))

    def testPendingIsUnindexed(self):
        self.workflow.doActionFor(self.folder.doc, 'submit')
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPublishedCanBeFound(self):
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.failUnless(self.catalog(id='doc'))

    def testPublishedIsUnindexed(self):
        # Works here!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPublishedIsUnindexedIfOwnerDeletes(self):
        # Works here!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        self.folder._delObject('doc')
        self.failIf(self.catalog(id='doc'))

    def testPublishedIsUnindexedByFolderDeleteScript(self):
        # Works here too!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        self.app.REQUEST.set('ids', ['doc'])
        self.folder.folder_delete()
        self.failIf(self.catalog(id='doc'))

    def testPublishedIsUnindexedWhenDeletingParentFolder(self):
        # Works here too!
        self.setRoles(['Manager'])
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.setRoles(['Member'])
        self.folder.aq_parent._delObject(self.folder.getId())
        self.failIf(self.catalog(id='doc'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCatalogTool))
    suite.addTest(makeSuite(TestCatalogSearch))
    suite.addTest(makeSuite(TestFolderCataloging))
    suite.addTest(makeSuite(TestCatalogBugs))
    suite.addTest(makeSuite(TestCatalogUnindexing))
    return suite

if __name__ == '__main__':
    framework()
