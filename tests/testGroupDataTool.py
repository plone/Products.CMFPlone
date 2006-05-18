#
# Tests for GRUF's GroupDataTool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

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
        self.prefix = self.acl_users.getGroupPrefix()
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        # MUST reset _v_ attributes!
        self.groupdata._v_temps = None

    def testWrapGroup(self):
        g = self.acl_users.getGroup(self.prefix+'foo')
        self.assertEqual(g.__class__.__name__, 'GRUFGroup')
        g = self.groupdata.wrapGroup(g)
        self.assertEqual(g.__class__.__name__, 'GroupData')
        self.assertEqual(g.aq_parent.__class__.__name__, 'GRUFGroup')
        self.assertEqual(g.aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')


class TestGroupData(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.memberdata = self.portal.portal_memberdata
        self.acl_users = self.portal.acl_users
        self.groups = self.portal.portal_groups
        self.groupdata = self.portal.portal_groupdata
        self.prefix = self.acl_users.getGroupPrefix()
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        # MUST reset _v_ attributes!
        self.memberdata._v_temps = None
        self.groupdata._v_temps = None

    def testGetGroup(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.__class__.__name__, 'GroupData')
        g = g.getGroup()
        self.assertEqual(g.__class__.__name__, 'GRUFGroup')

    def testGetTool(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.getTool().getId(), 'portal_groupdata')

    def testGetGroupMembers(self):
        g = self.groups.getGroupById('foo')
        self.acl_users._updateUser(default_user, groups=['foo'])
        self.assertEqual(g.getGroupMembers()[0].getId(), default_user)

    def testGroupMembersAreWrapped(self):
        g = self.groups.getGroupById('foo')
        self.acl_users._updateUser(default_user, groups=['foo'])
        ms = g.getGroupMembers()
        self.assertEqual(ms[0].__class__.__name__, 'MemberData')
        self.assertEqual(ms[0].aq_parent.__class__.__name__, 'GRUFUser')
        self.assertEqual(ms[0].aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')

    def testAddMember(self):
        g = self.groups.getGroupById('foo')
        g.addMember(default_user)
        self.assertEqual(g.getGroupMembers()[0].getId(), default_user)

    def testRemoveMember(self):
        g = self.groups.getGroupById('foo')
        g.addMember(default_user)
        g.removeMember(default_user)
        self.assertEqual(len(g.getGroupMembers()), 0)

    #def testSetProperties(self):
    #    # XXX: ERROR!
    #    g = self.groups.getGroupById('foo')
    #    g.setProperties(email='foo@bar.com')
    #    gd = self.groupdata._members[self.prefix+'foo']
    #    self.assertEqual(gd.email, 'foo@bar.com')

    def testSetGroupProperties(self):
        g = self.groups.getGroupById('foo')
        g.setGroupProperties({'email': 'foo@bar.com'})
        gd = self.groupdata._members[g.getId()]
        self.assertEqual(gd.email, 'foo@bar.com')

    def testSetMemberProperties(self):
        # For reference
        m = self.membership.getMemberById(default_user)
        m.setMemberProperties({'email': 'foo@bar.com'})
        md = self.memberdata._members[m.getId()]
        self.assertEqual(md.email, 'foo@bar.com')

    def testGetProperty(self):
        g = self.groups.getGroupById('foo')
        g.setGroupProperties({'email': 'foo@bar.com'})
        self.assertEqual(g.getProperty('email'), 'foo@bar.com')
        self.assertEqual(g.getProperty('id'), self.prefix+'foo')

    def testGetGroupName(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.getGroupName(), 'foo')

    def testGetGroupId(self):
        g = self.groups.getGroupById('foo')
        # This changed in GRUF3
        #self.assertEqual(g.getGroupId(), self.prefix+'foo')
        self.assertEqual(g.getGroupId(), 'foo')

    def testGetRoles(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.getRoles(), ('Authenticated',))
        self.acl_users._updateGroup(g.getId(), roles=['Member'])
        g = self.groups.getGroupById('foo')
        self.assertEqual(sortTuple(g.getRoles()), ('Authenticated', 'Member'))

    def testGetRolesInContext(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.getRolesInContext(self.folder), ('Authenticated',))
        self.folder.manage_setLocalRoles(g.getId(), ['Owner'])
        self.assertEqual(sortTuple(g.getRolesInContext(self.folder)), ('Authenticated', 'Owner'))

    def testGetDomains(self):
        g = self.groups.getGroupById('foo')
        self.assertEqual(g.getDomains(), ())

    def testHasRole(self):
        g = self.groups.getGroupById('foo')
        self.acl_users._updateGroup(g.getId(), roles=['Member'])
        g = self.groups.getGroupById('foo')
        self.failUnless(g.has_role('Member'))


from AccessControl import Unauthorized

class TestMethodProtection(PloneTestCase.PloneTestCase):
    # GroupData has wrong security declarations

    _unprotected = (
        'addMember',
        'removeMember',
    )

    def afterSetUp(self):
        self.groups = self.portal.portal_groups
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        self.groupdata = self.groups.getGroupById('foo')

    def assertUnprotected(self, object, method):
        self.logout()
        object.restrictedTraverse(method)

    def assertProtected(self, object, method):
        self.logout()
        self.assertRaises(Unauthorized, object.restrictedTraverse, method)

    def assertMemberProtected(self, object, method):
        self.assertRaises(Unauthorized, object.restrictedTraverse, method)

    for method in _unprotected:
        exec "def testAnonProtected_%s(self):" \
             "    self.assertProtected(self.groupdata, '%s')" % (method, method)

        exec "def testMemberProtected_%s(self):" \
             "    self.assertMemberProtected(self.groupdata, '%s')" % (method, method)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGroupDataTool))
    suite.addTest(makeSuite(TestGroupData))
    suite.addTest(makeSuite(TestMethodProtection))
    return suite

if __name__ == '__main__':
    framework()
