#
# Tests for GRUF's GroupsTool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Acquisition import aq_base

from Products.GroupUserFolder.GroupUserFolder import GroupUserFolder
from Products.GroupUserFolder.GroupUserFolder import manage_addGroupUserFolder
from Products.GroupUserFolder.GroupDataTool import GroupDataTool
from Products.GroupUserFolder.GroupsTool import GroupsTool

default_user = PloneTestCase.default_user

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestGroupsTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.acl_users = self.portal.acl_users
        self.groups = self.portal.portal_groups
        self.prefix = self.acl_users.getGroupPrefix()
        self.groups.groupWorkspacesCreationFlag = 0

        # Nuke Administators and Reviewers groups added in 2.1a2 migrations
        # (and any other migrated-in groups) to avoid test confusion
        self.groups.removeGroups(self.groups.listGroupIds())

    def testAddGroup(self):
        self.groups.addGroup('foo', [], [])
        self.assertEqual(self.groups.listGroupIds(), ['foo'])
        # No group workspace should have been created
        self.failIf(hasattr(aq_base(self.portal), self.groups.getGroupWorkspacesFolderId()))

    def testGetGroupById(self):
        self.groups.addGroup('foo', [], [])
        g = self.groups.getGroupById('foo')
        self.failIfEqual(g, None)

    def testGetBadGroupById(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g, None)

    def testGroupByIdIsWrapped(self):
        self.groups.addGroup('foo', [], [])
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.__class__.__name__, 'GroupData')
        self.assertEqual(g.aq_parent.__class__.__name__, 'GRUFGroup')
        self.assertEqual(g.aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')

    def testEditGroupAndGetGroupInfo(self):
        self.groups.addGroup('foo', )
        self.groups.editGroup('foo', roles = ['Reviewer'], title = 'A title', description = 'desc', email = 'f@foo.com') # => no domains on groups
        g = self.groups.getGroupById('foo')
        self.assertEqual(sortTuple(g.getRoles()), ('Authenticated', 'Reviewer'))
	info = self.groups.getGroupInfo('foo')
        self.assertEqual(info['title'], 'A title')	
        self.assertEqual(info['description'], 'desc')	
        self.assertEqual(info['email'], 'f@foo.com')	
        ##self.assertEqual(g.getDomains(), ('foo.com',))                  # No domains on groups
        ##self.assertEqual(g.getGroup()._getPassword(), 'secret')         # No password for groups

    def testGetBadGroupInfo(self):
	info = self.groups.getGroupInfo('foo')
        self.assertEqual(info, None)	

    def testEditBadGroup(self):
        # Error type depends on the user folder...
        try:
            self.groups.editGroup('foo', [], [])
        except KeyError:
            pass        # Ok, this is the wanted behaviour
        except ValueError:
            pass        # Ok, this is the wanted behaviour
        else:
            self.fail("Should have raised KeyError or ValueError")

    def testRemoveGroups(self):
        self.groups.addGroup('foo', [], [])
        self.groups.removeGroups(['foo'])
        self.assertEqual(len(self.groups.listGroupIds()), 0)

    def testListGroupIds(self):
        self.groups.addGroup('foo', [], [])
        self.groups.addGroup('bar', [], [])
        grps = self.groups.listGroupIds()
        grps.sort()
        self.assertEqual(grps, ['bar', 'foo'])

    def testGetGroupsByUserId(self):
        self.groups.addGroup('foo', [], [])
        self.acl_users._updateUser(default_user, groups=['foo'])
        gs = self.groups.getGroupsByUserId(default_user)
        self.assertEqual(gs[0].getId(), self.prefix + 'foo')

    def testGroupsByUserIdAreWrapped(self):
        self.groups.addGroup('foo', [], [])
        self.acl_users._updateUser(default_user, groups=['foo'])
        gs = self.groups.getGroupsByUserId(default_user)
        self.assertEqual(gs[0].__class__.__name__, 'GroupData')
        self.assertEqual(gs[0].aq_parent.__class__.__name__, 'GRUFGroup')
        self.assertEqual(gs[0].aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')

    def testListGroups(self):
        self.groups.addGroup('foo', [], [])
        self.groups.addGroup('bar', [], [])
        gs = self.groups.listGroups()
        self.assertEqual(gs[0].getId(), self.prefix + 'bar')
        self.assertEqual(gs[1].getId(), self.prefix + 'foo')

    def testListedGroupsAreWrapped(self):
        self.groups.addGroup('foo', [], [])
        gs = self.groups.listGroups()
        self.assertEqual(gs[0].__class__.__name__, 'GroupData')
        self.assertEqual(gs[0].aq_parent.__class__.__name__, 'GRUFGroup')
        self.assertEqual(gs[0].aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')

    # This should not be in a groups tool!
    ##def testGetPureUserNames(self):
    ##    self.groups.addGroup('foo', [], [])
    ##    self.assertEqual(len(self.acl_users.getUserNames()), 2)
    ##    self.assertEqual(len(self.groups.getPureUserNames()), 1)

    # This should not be in a groups tool!
    ##def testGetPureUsers(self):
    ##    self.groups.addGroup('foo', [], [])
    ##    self.assertEqual(len(self.acl_users.getUsers()), 2)
    ##    self.assertEqual(len(self.groups.getPureUsers()), 1)

    # This should not be in a groups tool!
    ##def testPureUsersAreNotWrapped(self):
    ##    self.groups.addGroup('foo', [], [])
    ##    us = self.groups.getPureUsers()
    ##    self.assertEqual(us[0].__class__.__name__, 'GRUFGroup')
    ##    self.assertEqual(us[0].aq_parent.__class__.__name__, 'GroupUserFolder')

    def testSetGroupOwnership(self):
        self.groups.addGroup('foo', [], [])
        self.folder.invokeFactory('Document', 'doc')
        doc = self.folder.doc
        g = self.groups.getGroupById('foo')
        self.groups.setGroupOwnership(g, doc)
        self.assertEqual(doc.getOwnerTuple()[1], self.prefix + 'foo')
        self.assertEqual(doc.get_local_roles_for_userid(self.prefix + 'foo'), ('Owner',))
        # XXX: Initial creator still has Owner role. Is this a bug?
        self.assertEqual(doc.get_local_roles_for_userid(default_user), ('Owner',))

    def testWrapGroup(self):
        self.groups.addGroup('foo', [], [])
        g = self.acl_users.getGroup(self.prefix + 'foo')
        self.assertEqual(g.__class__.__name__, 'GRUFGroup')
        g = self.groups.wrapGroup(g)
        self.assertEqual(g.__class__.__name__, 'GroupData')
        self.assertEqual(g.aq_parent.__class__.__name__, 'GRUFGroup')
        self.assertEqual(g.aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')


class TestGroupWorkspacesFolder(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.acl_users = self.portal.acl_users
        self.groups = self.portal.portal_groups
        self.prefix = self.acl_users.getGroupPrefix()
        self.groups.groupWorkspacesCreationFlag = 0
        # Note that this is not a proper portal type (anymore) but we don't care
        self.portal.manage_addPortalFolder(self.groups.getGroupWorkspacesFolderId())

        # Nuke Administators and Reviewers groups added in 2.1a2 migrations
        # (and any other migrated-in groups) to avoid test confusion
        self.groups.removeGroups(self.groups.listGroupIds())

    def testGetGroupWorkspacesFolder(self):
        self.failIfEqual(self.groups.getGroupWorkspacesFolder(), None)

    def testCreateGrouparea(self):
        self.groups.addGroup('foo', [], [])
        self.groups.toggleGroupWorkspacesCreation()
        # XXX: Requires typestool
        self.groups.createGrouparea('foo')
        self.failUnless(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))

    def testNotCreateGrouparea(self):
        self.groups.addGroup('foo', [], [])
        # Creation flag is False
        self.groups.createGrouparea('foo')
        self.failIf(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))

    def testCreateGroupareaCreatesGroupWorkspacesFolder(self):
        self.groups.addGroup('foo', [], [])
        self.groups.toggleGroupWorkspacesCreation()
        self.portal._delObject(self.groups.getGroupWorkspacesFolderId())
        # XXX: Members cannot create folders in the portal root
        self.setRoles(['Manager'])
        self.groups.createGrouparea('foo')
        self.failUnless(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))

    def testAddGroupCreatesGrouparea(self):
        self.groups.toggleGroupWorkspacesCreation()
        self.groups.addGroup('foo', [], [])
        self.failUnless(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))

    def testGetGroupareaFolder(self):
        self.groups.toggleGroupWorkspacesCreation()
        self.groups.addGroup('foo', [], [])
        self.failIfEqual(self.groups.getGroupareaFolder('foo'), None)

    def testGetGroupareaURL(self):
        self.groups.toggleGroupWorkspacesCreation()
        self.groups.addGroup('foo', [], [])
        self.failIfEqual(self.groups.getGroupareaURL('foo'), None)

    def testGetGroupareaFolderPermission(self):
        self.groups.toggleGroupWorkspacesCreation()
        self.groups.addGroup('foo', [], [])
        self.acl_users._updateUser(default_user, groups=['foo'])
        user = self.acl_users.getUser(default_user)
        self.login()   # !!! Fixed in Zope 2.6.2
        self.failUnless(user.has_permission('View Groups', self.groups.getGroupWorkspacesFolder()))

    #def testGetGroupareaFolderForAuthenticated(self):
    #    # XXX: ERROR!
    #    self.groups.toggleGroupWorkspacesCreation()
    #    self.groups.addGroup('foo', [], [])
    #    self.acl_users._updateUser(default_user, groups=['foo'])
    #    self.login(default_user)
    #    self.failIfEqual(self.groups.getGroupareaFolder(), None)

    def testAddGroup(self):
        self.groups.addGroup('foo', [], [])
        self.assertEqual(self.groups.listGroupIds(), ['foo'])
        # No group workspace should have been created
        self.failIf(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))

    def testAddGroupWithWorkspace(self):
        self.groups.toggleGroupWorkspacesCreation()
        self.groups.addGroup('foo', [], [])
        self.assertEqual(self.groups.listGroupIds(), ['foo'])
        # A group workspace should have been created
        self.failUnless(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))

    def testRemoveGroups(self):
        self.groups.addGroup('foo', [], [])
        self.groups.removeGroups(['foo'])
        self.assertEqual(len(self.groups.listGroupIds()), 0)

    def testRemoveGroupsWithWorkspace(self):
        self.groups.toggleGroupWorkspacesCreation()
        self.groups.addGroup('foo', [], [])
        self.groups.removeGroups(['foo'])
        self.assertEqual(len(self.groups.listGroupIds()), 0)
        # Group workspace should have been removed
        self.failIf(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))

    def testRemoveGroupsKeepingWorkspaces(self):
        self.groups.toggleGroupWorkspacesCreation()
        self.groups.addGroup('foo', [], [])
        self.groups.removeGroups(['foo'], keep_workspaces=1)
        self.assertEqual(len(self.groups.listGroupIds()), 0)
        # Group workspace should still be present
        self.failUnless(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGroupsTool))
    suite.addTest(makeSuite(TestGroupWorkspacesFolder))
    return suite

if __name__ == '__main__':
    framework()
