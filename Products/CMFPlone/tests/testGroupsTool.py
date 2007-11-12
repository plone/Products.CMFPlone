#
# Tests for GRUF's GroupsTool
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.tests.base.testcase import WarningInterceptor

from Acquisition import aq_base

default_user = PloneTestCase.default_user

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestGroupsTool(PloneTestCase.PloneTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.acl_users = self.portal.acl_users
        self.groups = self.portal.portal_groups
        self.groups.groupWorkspacesCreationFlag = 0
        self._trap_warning_output()

        if 'auto_group' in self.acl_users.objectIds():
            self.acl_users.manage_delObjects(['auto_group'])

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
        self.assertEqual(g.aq_parent.__class__.__name__, 'PloneGroup')
        self.assertEqual(g.aq_parent.aq_parent.__class__.__name__, 'GroupManager')

    def testEditGroup(self):
        self.groups.addGroup('foo', )
        self.groups.editGroup('foo', roles = ['Reviewer']) #, ['foo.com']) => no domains on groups
        g = self.groups.getGroupById('foo')
        self.assertEqual(sortTuple(g.getRoles()), ('Authenticated', 'Reviewer'))
        ##self.assertEqual(g.getDomains(), ('foo.com',))                  # No domains on groups
        ##self.assertEqual(g.getGroup()._getPassword(), 'secret')         # No password for groups

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
        self.acl_users.userSetGroups(default_user, groupnames=['foo'])
        gs = self.groups.getGroupsByUserId(default_user)
        self.assertEqual(gs[0].getId(), 'foo')

    def testGroupsByUserIdAreWrapped(self):
        self.groups.addGroup('foo', [], [])
        self.acl_users.userSetGroups(default_user, groupnames=['foo'])
        gs = self.groups.getGroupsByUserId(default_user)
        self.assertEqual(gs[0].__class__.__name__, 'GroupData')
        self.assertEqual(gs[0].aq_parent.__class__.__name__, 'PloneGroup')
        self.assertEqual(gs[0].aq_parent.aq_parent.__class__.__name__, 'GroupManager')

    def testListGroups(self):
        self.groups.addGroup('foo', [], [])
        self.groups.addGroup('bar', [], [])
        gs = self.groups.listGroups()
        self.assertEqual(gs[0].getId(), 'bar')
        self.assertEqual(gs[1].getId(), 'foo')

    def testListedGroupsAreWrapped(self):
        self.groups.addGroup('foo', [], [])
        gs = self.groups.listGroups()
        self.assertEqual(gs[0].__class__.__name__, 'GroupData')
        self.assertEqual(gs[0].aq_parent.__class__.__name__, 'PloneGroup')
        self.assertEqual(gs[0].aq_parent.aq_parent.__class__.__name__, 'GroupManager')

    def testSetGroupOwnership(self):
        self.groups.addGroup('foo', [], [])
        self.folder.invokeFactory('Document', 'doc')
        doc = self.folder.doc
        g = self.groups.getGroupById('foo')
        self.groups.setGroupOwnership(g, doc)
        self.assertEqual(doc.getOwnerTuple()[1], 'foo')
        self.assertEqual(doc.get_local_roles_for_userid('foo'), ('Owner',))
        # TODO: Initial creator still has Owner role. Is this a bug?
        self.assertEqual(doc.get_local_roles_for_userid(default_user), ('Owner',))

    def testWrapGroup(self):
        self.groups.addGroup('foo', [], [])
        g = self.acl_users.getGroup('foo')
        self.assertEqual(g.__class__.__name__, 'PloneGroup')
        g = self.groups.wrapGroup(g)
        self.assertEqual(g.__class__.__name__, 'GroupData')
        self.assertEqual(g.aq_parent.__class__.__name__, 'PloneGroup')
        self.assertEqual(g.aq_parent.aq_parent.__class__.__name__, 'GroupManager')

    def testGetGroupInfo(self):
        self.groups.addGroup('foo', title='Foo', description='Bar', email='foo@foo.com')
        info = self.groups.getGroupInfo('foo')
        self.assertEqual(info.get('title'), 'Foo')
        self.assertEqual(info.get('description'), 'Bar')
        self.assertEqual(info.get('email'), None) # No email!

    def testGetGroupInfoAsAnonymous(self):
        self.groups.addGroup('foo', title='Foo', description='Bar')
        self.logout()
        info = self.groups.restrictedTraverse('getGroupInfo')('foo')
        self.assertEqual(info.get('title'), 'Foo')
        self.assertEqual(info.get('description'), 'Bar')

    def testGetBadGroupInfo(self):
        info = self.groups.getGroupInfo('foo')
        self.assertEqual(info, None)

    def beforeTearDown(self):
        self._free_warning_output()


class TestGroupWorkspacesFolder(PloneTestCase.PloneContentLessTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.acl_users = self.portal.acl_users
        self.groups = self.portal.portal_groups
        self.groups.groupWorkspacesCreationFlag = 0
        self._trap_warning_output()

        if 'auto_group' in self.acl_users.objectIds():
            self.acl_users.manage_delObjects(['auto_group'])
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
        # TODO: Requires typestool
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
        # Members cannot create folders in the portal root
        self.setRoles(['Manager'])
        self.groups.createGrouparea('foo')
        self.failUnless(hasattr(aq_base(self.groups.getGroupWorkspacesFolder()), 'foo'))

    def testCreateGroupareaIndexesGroupWorkspacesFolder(self):
        self.groups.addGroup('foo', [], [])
        self.groups.toggleGroupWorkspacesCreation()
        self.portal._delObject(self.groups.getGroupWorkspacesFolderId())
        # Members cannot create folders in the portal root
        self.setRoles(['Manager'])
        self.groups.createGrouparea('foo')
        cat_results = self.portal.portal_catalog(getId =
                                     self.groups.getGroupWorkspacesFolderId())
        self.assertEqual(len(cat_results), 1)
        self.assertEqual(cat_results[0].getObject(),
                                       self.groups.getGroupWorkspacesFolder())

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
        self.acl_users.userSetGroups(default_user, groupnames=['foo'])
        user = self.acl_users.getUser(default_user)
        self.failUnless(user.has_permission('View Groups', self.groups.getGroupWorkspacesFolder()))

    #def testGetGroupareaFolderForAuthenticated(self):
    #    # XXX: ERROR!
    #    self.groups.toggleGroupWorkspacesCreation()
    #    self.groups.addGroup('foo', [], [])
    #    self.acl_users.userSetGroups(default_user, groupnames=['foo'])
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

    def beforeTearDown(self):
        self._free_warning_output()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGroupsTool))
    suite.addTest(makeSuite(TestGroupWorkspacesFolder))
    return suite
