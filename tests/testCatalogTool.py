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

user1 = ZopeTestCase._user_name
user2 = 'u2'


class TestCatalogTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog

    def loginAsPortalOwner(self):
        from AccessControl.SecurityManagement import newSecurityManager
        uf = self.app.acl_users
        user = uf.getUserById('PloneTestCase').__of__(uf)
        newSecurityManager(None, user)

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
        self.loginAsPortalOwner()
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


class TestCatalogSearch(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

    def addLocalGroupAndUser(self):
        # utility for
        uf = self.portal.acl_users
        prefix = uf.getGroupPrefix()
        groupname = 'extranet' #% prefix
        groups = self.portal.portal_groups
        groups.groupWorkspacesCreationFlag = 0
        groups.addGroup(groupname, None, [], ())
        assert len( uf.getGroups()) == 1
        group=groups.getGroupById(groupname)
        group.addMember(user2)
        assert(group.getGroupMembers()[0].getUserName() == user2)
        # mind you, do not get the user before she was added to the group, 
        # or she will not have any groups
        user = uf.getUser(user2)
        assert user.getGroups()[0] == '%s%s' % (prefix,groupname)
        return '%s%s' % (prefix,groupname)

    def addUser2AndDocument(self):
        uf = self.portal.acl_users
        uf._doAddUser(user2, 'secret', (), (), (), )
        self.folder.invokeFactory('Document', id='testdocument', text='nonsense')
        self.workflow.doActionFor(self.folder.testdocument, 'hide', comment='')

    def testListAllowedRolesAndUsers(self):
        # should add group to list of allowed users
        uf = self.portal.acl_users
        uf._doAddUser(user2, 'secret', (), (), (), )
        groupname = self.addLocalGroupAndUser()
        self.failUnless(('user:%s' % groupname) in 
                self.catalog._listAllowedRolesAndUsers(uf.getUser(user2)))

    def testSearchReturnsDocument(self):
        # document should be found when owner does a search
        self.addUser2AndDocument()
        self.assertEqual(self.catalog({'SearchableText':'nonsense'})[0].id,
                         'testdocument')

    def testSearchDoesNotReturnDocument(self):
        # document should not be found when user 2 does a search
        self.addUser2AndDocument()
        self.login(user2)
        self.assertEqual(len(self.catalog({'SearchableText':'nonsense'})), 0)

    def testSearchReturnsDocumentWhenPermissionIsTroughLocalRole2(self):
        # after adding a local group with access rights and adding user2 search must find document
        self.addUser2AndDocument()
        groupname = self.addLocalGroupAndUser()
        self.folder.folder_localrole_edit('add', [groupname], 'Owner')
        # login again as user 2. a search now must get the document
        self.login(user2)
        self.assertEqual(self.catalog({'SearchableText':'nonsense'})[0].id,
                         'testdocument')


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCatalogTool))
        suite.addTest(unittest.makeSuite(TestCatalogSearch))
        return suite

