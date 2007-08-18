#
# Tests for GRUF's GroupDataTool
#

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFCore.tests.base.testcase import WarningInterceptor

from AccessControl import Unauthorized
from AccessControl import Permissions

default_user = PloneTestCase.default_user

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)


class TestGroupDataTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.acl_users = self.portal.acl_users
        self.groups = self.portal.portal_groups
        self.groupdata = self.portal.portal_groupdata
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        # MUST reset _v_ attributes!
        self.groupdata._v_temps = None
        if 'auto_group' in self.acl_users.objectIds():
            self.acl_users.manage_delObjects(['auto_group'])

    def testWrapGroup(self):
        g = self.acl_users.getGroup('foo')
        self.assertEqual(g.__class__.__name__, 'PloneGroup')
        g = self.groupdata.wrapGroup(g)
        self.assertEqual(g.__class__.__name__, 'GroupData')
        self.assertEqual(g.aq_parent.__class__.__name__, 'PloneGroup')
        self.assertEqual(g.aq_parent.aq_parent.__class__.__name__, 'GroupManager')


class TestGroupData(PloneTestCase.PloneTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.memberdata = self.portal.portal_memberdata
        self.acl_users = self.portal.acl_users
        self.groups = self.portal.portal_groups
        self.groupdata = self.portal.portal_groupdata
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        if 'auto_group' in self.acl_users.objectIds():
            self.acl_users.manage_delObjects(['auto_group'])
        # MUST reset _v_ attributes!
        self.memberdata._v_temps = None
        self.groupdata._v_temps = None
        self._trap_warning_output()

    def testGetGroup(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.__class__.__name__, 'GroupData')
        g = g.getGroup()
        self.assertEqual(g.__class__.__name__, 'PloneGroup')

    def testGetTool(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.getTool().getId(), 'portal_groupdata')

    def testGetGroupMembers(self):
        g = self.groups.getGroupById('foo')
        self.acl_users.userSetGroups(default_user, groupnames=['foo'])
        self.assertEqual(g.getGroupMembers()[0].getId(), default_user)

    def testGroupMembersAreWrapped(self):
        g = self.groups.getGroupById('foo')
        self.acl_users.userSetGroups(default_user, groupnames=['foo'])
        ms = g.getGroupMembers()
        self.assertEqual(ms[0].__class__.__name__, 'MemberData')
        self.assertEqual(ms[0].aq_parent.__class__.__name__, 'PloneUser')
        self.assertEqual(ms[0].aq_parent.aq_parent.__class__.__name__, 'PluggableAuthService')

    def testAddMember(self):
        self.setPermissions([Permissions.manage_users])
        g = self.groups.getGroupById('foo')
        g.addMember(default_user)
        self.assertEqual(g.getGroupMembers()[0].getId(), default_user)

    def testRemoveMember(self):
        self.setPermissions([Permissions.manage_users])
        g = self.groups.getGroupById('foo')
        g.addMember(default_user)
        g.removeMember(default_user)
        self.assertEqual(len(g.getGroupMembers()), 0)

    def testSetGroupProperties(self):
        g = self.groups.getGroupById('foo')
        g.setGroupProperties({'email': 'foo@bar.com'})
        gd = self.groups.getGroupById('foo')
        self.assertEqual(gd.getProperty('email'), 'foo@bar.com')

    def testSetMemberProperties(self):
        # For reference
        m = self.membership.getMemberById(default_user)
        m.setMemberProperties({'email': 'foo@bar.com'})
        md = self.membership.getMemberById(default_user)
        self.assertEqual(md.getProperty('email'), 'foo@bar.com')

    def testGetProperty(self):
        g = self.groups.getGroupById('foo')
        g.setGroupProperties({'email': 'foo@bar.com'})
        self.assertEqual(g.getProperty('email'), 'foo@bar.com')
        self.assertEqual(g.getProperty('id'), 'foo')

    def testGetGroupName(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.getGroupName(), 'foo')

    def testGetGroupId(self):
        g = self.groups.getGroupById('foo')
        # This changed in GRUF3
        #self.assertEqual(g.getGroupId(), 'foo')
        self.assertEqual(g.getGroupId(), 'foo')

    def testGetRoles(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(tuple(g.getRoles()), ('Authenticated',))
        self.groups.editGroup(g.getId(), roles=['Member'])
        g = self.groups.getGroupById('foo')
        self.assertEqual(sortTuple(tuple(g.getRoles())), ('Authenticated', 'Member'))

    def testGetRolesInContext(self):
        g = self.groups.getGroupById('foo')
        self.acl_users.userSetGroups(default_user, groupnames=['foo'])
        user = self.acl_users.getUser(default_user)
        self.assertEqual(user.getRolesInContext(self.folder).sort(),
                        ['Member', 'Authenticated', 'Owner'].sort())
        self.folder.manage_setLocalRoles(g.getId(), ['NewRole'])
        self.assertEqual(user.getRolesInContext(self.folder).sort(), 
                        ['Member', 'Authenticated', 'Owner', 'NewRole'].sort())

    def testGetDomains(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.getDomains(), ())

    def testHasRole(self):
        g = self.groups.getGroupById('foo')
        self.groups.editGroup(g.getId(), roles=['Member'])
        g = self.groups.getGroupById('foo')
        self.failUnless(g.has_role('Member'))

    def beforeTearDown(self):
        self._free_warning_output()


class TestMethodProtection(PloneTestCase.PloneTestCase):
    # GroupData has wrong security declarations

    def afterSetUp(self):
        self.groups = self.portal.portal_groups
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        self.groupdata = self.groups.getGroupById('foo')

    def testAnonAddMember(self):
        self.logout()
        self.assertRaises(Unauthorized, self.groupdata.addMember, default_user)

    def testAnonRemoveMember(self):
        self.logout()
        self.assertRaises(Unauthorized, self.groupdata.removeMember, default_user)

    def testMemberAddMember(self):
        self.assertRaises(Unauthorized, self.groupdata.addMember, default_user)

    def testMemberRemoveMember(self):
        self.assertRaises(Unauthorized, self.groupdata.removeMember, default_user)

    def testManagerAddMember(self):
        self.setPermissions([Permissions.manage_users])
        self.groupdata.addMember(default_user)

    def testManagerRemoveMember(self):
        self.setPermissions([Permissions.manage_users])
        self.groupdata.addMember(default_user)
        self.groupdata.removeMember(default_user)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGroupDataTool))
    suite.addTest(makeSuite(TestGroupData))
    suite.addTest(makeSuite(TestMethodProtection))
    return suite
