#
# MembershipTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

default_user = PloneTestCase.default_user


class TestMembershipTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership

    def testGetPersonalFolder(self):
        # Should return the .personal folder
        personal = getattr(self.folder, self.membership.personal_id, None)
        self.failIfEqual(personal, None)
        self.assertEqual(self.membership.getPersonalFolder(default_user), personal)

    def testGetPersonalFolderIfMissing(self):
        # Should return None as the .personal folder is missing
        self.folder._delObject(self.membership.personal_id)
        self.assertEqual(self.membership.getPersonalFolder(default_user), None)

    def testGetPersonalFolderIfNoHome(self):
        # Should return None as the user has no home folder
        members = self.membership.getMembersFolder()
        members._delObject(default_user)
        self.assertEqual(self.membership.getPersonalFolder(default_user), None)

    def testGetPersonalPortrait(self):
        # Should return the default portrait
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), 'defaultUser.gif')

    def testChangeMemberPortrait(self):
        # Should change the portrait image
        self.membership.changeMemberPortrait(Portrait(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).meta_type, 'Image')

    def testDeletePersonalPortrait(self):
        # Should delete the portrait image
        self.membership.changeMemberPortrait(Portrait(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), default_user)
        self.membership.deletePersonalPortrait(default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), 'defaultUser.gif')

    def testGetPersonalPortraitWithoutPassingId(self):
        # Should return the logged in users portrait if no id is given
        self.membership.changeMemberPortrait(Portrait(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait().getId(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait().meta_type, 'Image')

    def testListMembers(self):
        # Should return the members list
        members = self.membership.listMembers()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].getId(), default_user)

    def testListMembersSkipsGroups(self):
        # Should only return real members, not groups
        uf = self.portal.acl_users
        uf.changeOrCreateGroups(new_groups=['Foo', 'Bar'])
        self.assertEqual(len(uf.getUserNames()), 3)
        members = self.membership.listMembers()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].getId(), default_user)

    def testListMemberIds(self):
        # Should return the members ids list
        memberids = self.membership.listMemberIds()
        self.assertEqual(len(memberids), 1)
        self.assertEqual(memberids[0], default_user)

    def testListMemberIdsSkipsGroups(self):
        # Should only return real members, not groups
        uf = self.portal.acl_users
        uf.changeOrCreateGroups(new_groups=['Foo', 'Bar'])
        self.assertEqual(len(uf.getUserNames()), 3)
        memberids = self.membership.listMemberIds()
        self.assertEqual(len(memberids), 1)
        self.assertEqual(memberids[0], default_user)

    def testCurrentPassword(self):
        # Password checking should work
        self.failUnless(self.membership.testCurrentPassword('secret'))
        self.failIf(self.membership.testCurrentPassword('geheim'))

    def testSetPassword(self):
        # Password should be changed
        self.membership.setPassword('geheim')
        self.failUnless(self.membership.testCurrentPassword('geheim'))

    def testSetPasswordIfAnonymous(self):
        # Anonymous should not be able to change password
        self.logout()
        try:
            self.membership.setPassword('geheim')
        except:
            # Bl**dy string exceptions
            import sys; e, v, tb = sys.exc_info(); del tb
            if str(e) == 'Bad Request' and str(v) == 'Not logged in.':
                pass    # Test passed
            else:
                raise

    def testSetPasswordAndKeepGroups(self):
        # Password should be changed and user must not change group membership
        group2 = 'g2'
        groups = self.portal.portal_groups
        groups.groupWorkspacesCreationFlag = 0
        groups.addGroup(group2, None, [], [])
        group = groups.getGroupById(group2)
        group.addMember(default_user)
        ugroups = self.portal.acl_users.getUserById(default_user).getGroups()
        self.membership.setPassword('geheim')
        self.failUnless(self.portal.acl_users.getUserById(default_user).getGroups() == ugroups)

    def testWrapUserCreatesMemberarea(self):
        # This test serves to trip us up should this ever change
        # Also see http://plone.org/collector/1697
        uf = self.portal.acl_users
        uf._doAddUser('user2', 'secret', ['Member'], [])
        user = uf.getUserById('user2').__of__(uf)
        self.membership.wrapUser(user)
        memberfolder = self.membership.getHomeFolder('user2')
        self.failUnless(memberfolder, 'wrapUser failed to create memberarea')

    def testGetMemberById(self):
        # This should work for portal users,
        self.failIfEqual(self.membership.getMemberById(default_user), None)
        # return None for unknown users,
        self.assertEqual(self.membership.getMemberById('foo'), None)
        # and return None for users defined outside of the portal.
        self.assertEqual(self.membership.getMemberById(PloneTestCase.portal_owner), None)


# Fake upload object

class Portrait:
    filename = 'foo.gif'
    def seek(*args): pass
    def tell(*args): return 0
    def read(*args): return 'bar'


if __name__ == '__main__':
    framework()
else:
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestMembershipTool))
        return suite
