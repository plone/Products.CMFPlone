#
# CatalogTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base

_user_name = ZopeTestCase._user_name
user2 = 'u2'

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
    # mind you, do not get the user before she was added to the group, or she will not have any groups
    user = uf.getUser(user2)
    assert user.getGroups()[0] == '%s%s' % (prefix,groupname)
    return '%s%s' % (prefix,groupname)

def addUser2AndDocument(self):
    uf = self.portal.acl_users
    uf._doAddUser(user2, 'secret', (), (), (), )
    self.portal.portal_types.constructContent('Document', self.folder, 'testdocument', None, )
    document = self.folder.testdocument
    document.edit(document.text_format, text='user u2 added some nonsense')
    self.portal.portal_workflow.doActionFor(document, 'hide', comment='')


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

    def testManageAfterAddIfLexiconExists(self):
        # Should be able to copy/paste a portal containing
        # a catalog tool. Triggers manage_afterAdd of portal_catalog
        # thereby exposing a bug which is now going to be fixed.
        from AccessControl.SecurityManagement import newSecurityManager
        user = self.app.acl_users.getUserById('PloneTestCase').__of__(self.app.acl_users)
        newSecurityManager(None, user)
        cb = self.app.manage_copyObjects(['portal'])
        self.app.manage_pasteObjects(cb)
        self.failUnless(hasattr(self.app, 'copy_of_portal'))

    def test_listAllowedRolesAndUsers(self):
        # should add group to list of allowed users
        uf = self.portal.acl_users
        uf._doAddUser(user2, 'secret', (), (), (), )
        groupname = addLocalGroupAndUser(self)
        assert ('user:%s' % groupname) in self.catalog._listAllowedRolesAndUsers(self.portal.acl_users.getUser(user2))

    def testSearchReturnsDocument(self):
        # document should be found when owner does a search
        addUser2AndDocument(self)
        assert self.catalog({'SearchableText':'nonsense'})[0].getObject().getId() == 'testdocument'

    def testSearchDoesNotReturnDocument(self):
        # document should not be found when user 2 does a search
        addUser2AndDocument(self)
        self.login(user2)
        assert len(self.catalog({'SearchableText':'nonsense'})) == 0

    def testSearchReturnsDocumentWhenPermissionIsTroughLocalRole2(self):
        # after adding a local group with access rights and adding user2 search must find document
        addUser2AndDocument(self)
        groupname = addLocalGroupAndUser(self)
        self.folder.folder_localrole_edit('add', [groupname], 'Owner')
        # login again as user 2. a search now must get the document
        self.login(user2)
        assert self.catalog({'SearchableText':'nonsense'})[0].getObject().getId() == 'testdocument'


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCatalogTool))
        return suite

