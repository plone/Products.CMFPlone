#
# MembershipTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

_user_name = ZopeTestCase._user_name


# Fake upload object
class Portrait:
    filename = 'foo.gif'
    def seek(*args): pass
    def tell(*args): return 0
    def read(*args): return 'bar'


class TestMembershipTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership

    def testGetPersonalFolder(self):
        # Should return the .personal folder
        personal = getattr(self.folder, self.membership.personal_id, None)
        self.failIfEqual(personal, None)
        self.assertEqual(self.membership.getPersonalFolder(_user_name), personal)
         
    def testGetPersonalFolderIfMissing(self):
        # Should return None as the .personal folder is missing
        self.folder._delObject(self.membership.personal_id)
        self.assertEqual(self.membership.getPersonalFolder(_user_name), None)

    def testGetPersonalFolderIfNoHome(self):
        # Should return None as the user has no home folder
        members = self.membership.getMembersFolder()
        members._delObject(_user_name)
        self.assertEqual(self.membership.getPersonalFolder(_user_name), None)

    def testGetPersonalPortrait(self):
        # Should return the default portrait
        self.assertEqual(self.membership.getPersonalPortrait(_user_name).getId(), 'defaultUser.gif')

    def testChangeMemberPortrait(self):
        # Should change the portrait image
        self.membership.changeMemberPortrait(Portrait(), _user_name)
        self.assertEqual(self.membership.getPersonalPortrait(_user_name).getId(), _user_name)
        self.assertEqual(self.membership.getPersonalPortrait(_user_name).meta_type, 'Image')

    def testDeletePersonalPortrait(self):
        # Should delete the portrait image
        self.membership.changeMemberPortrait(Portrait(), _user_name)
        self.assertEqual(self.membership.getPersonalPortrait(_user_name).getId(), _user_name)
        self.membership.deletePersonalPortrait(_user_name)
        self.assertEqual(self.membership.getPersonalPortrait(_user_name).getId(), 'defaultUser.gif')

    def testGetPersonalPortraitWithoutPassingId(self):
        # Should return the logged in users portrait if no id is given
        self.membership.changeMemberPortrait(Portrait(), _user_name)
        self.assertEqual(self.membership.getPersonalPortrait().getId(), _user_name)
        self.assertEqual(self.membership.getPersonalPortrait().meta_type, 'Image')

    def testListMembers(self):
        # Should return the members list
        members = self.membership.listMembers()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].getId(), _user_name)

    def testListMembersSkipsGroups(self):
        # Should only return real members, not groups
        uf = self.portal.acl_users
        uf.changeOrCreateGroups(new_groups=['Foo', 'Bar'])
        self.assertEqual(len(uf.getUserNames()), 3)
        members = self.membership.listMembers()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0].getId(), _user_name)

    def testListMemberIds(self):
        # Should return the members ids list
        memberids = self.membership.listMemberIds()
        self.assertEqual(len(memberids), 1)
        self.assertEqual(memberids[0], _user_name)

    def testListMemberIdsSkipsGroups(self):
        # Should only return real members, not groups
        uf = self.portal.acl_users
        uf.changeOrCreateGroups(new_groups=['Foo', 'Bar'])
        self.assertEqual(len(uf.getUserNames()), 3)
        memberids = self.membership.listMemberIds()
        self.assertEqual(len(memberids), 1)
        self.assertEqual(memberids[0], _user_name)

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

    def testWrapUserCreatesMemberarea(self):
        # This test serves to trip us up should this ever change
        # Also see http://plone.org/collector/1697
        uf = self.portal.acl_users
        uf._doAddUser('user2', 'secret', ['Member'], [])
        user = uf.getUserById('user2').__of__(uf)
        self.membership.wrapUser(user)
        memberfolder = self.membership.getHomeFolder('user2')
        self.failUnless(memberfolder, 'wrapUser failed to create memberarea')


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestMembershipTool))
        return suite

