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

user1 = PloneTestCase.default_user
user2 = 'u2'
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

    def testCanPastePortalIfLexiconExists(self):
        # Should be able to copy/paste a portal containing
        # a catalog tool. Triggers manage_afterAdd of portal_catalog
        # thereby exposing a bug which is now going to be fixed.
        self.loginPortalOwner()
        cb = self.app.manage_copyObjects(['portal'])
        self.app.manage_pasteObjects(cb)
        self.failUnless(hasattr(self.app, 'copy_of_portal'))

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
        self.app.manage_renameObjects(['portal'], ['foo'])
        self.failUnless(hasattr(self.app, 'foo'))


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


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCatalogTool))
        suite.addTest(unittest.makeSuite(TestCatalogSearch))
        return suite

