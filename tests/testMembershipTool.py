#
# MembershipTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from AccessControl.User import nobody
from Acquisition import aq_base
from DateTime import DateTime
from zExceptions import BadRequest

default_user = PloneTestCase.default_user


class TestMembershipTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        
        # Nuke Administators and Reviewers groups added in 2.1a2 migrations
        # (and any other migrated-in groups) to avoid test confusion
        self.portal.portal_groups.removeGroups(self.portal.portal_groups.listGroupIds())

    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})

    def testNoMorePersonalFolder(self):
        personal = getattr(self.folder, self.membership.personal_id, None)
        self.assertEqual(personal, None)
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
        self.membership.changeMemberPortrait(dummy.File(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).meta_type, 'Image')

    def testDeletePersonalPortrait(self):
        # Should delete the portrait image
        self.membership.changeMemberPortrait(dummy.File(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), default_user)
        self.membership.deletePersonalPortrait(default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), 'defaultUser.gif')

    def testGetPersonalPortraitWithoutPassingId(self):
        # Should return the logged in users portrait if no id is given
        self.membership.changeMemberPortrait(dummy.File(), default_user)
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
        except BadRequest:
            import sys; e, v, tb = sys.exc_info(); del tb
            if str(v) == 'Not logged in.':
                pass
            else:
                raise

    def testSetPasswordAndKeepGroups(self):
        # Password should be changed and user must not change group membership
        group2 = 'g2'
        groups = self.portal.portal_groups
        groups.addGroup(group2, None, [], [])
        group = groups.getGroupById(group2)
        group.addMember(default_user)
        ugroups = self.portal.acl_users.getUserById(default_user).getGroups()
        self.membership.setPassword('geheim')
        self.failUnless(self.portal.acl_users.getUserById(default_user).getGroups() == ugroups)

    def testGetMemberById(self):
        # This should work for portal users,
        self.failIfEqual(self.membership.getMemberById(default_user), None)
        # return None for unknown users,
        self.assertEqual(self.membership.getMemberById('foo'), None)
        # and return None for users defined outside of the portal.
        ##self.assertEqual(self.membership.getMemberById(PloneTestCase.portal_owner), None)
        # Since CMF 1.5.2 the membershiptool will search "up"
        self.failIfEqual(self.membership.getMemberById(PloneTestCase.portal_owner), None)

    def testGetMemberByIdIsWrapped(self):
        member = self.membership.getMemberById(default_user)
        self.failIfEqual(member, None)
        self.assertEqual(member.__class__.__name__, 'MemberData')
        self.assertEqual(member.aq_parent.__class__.__name__, 'GRUFUser')

    def testGetAuthenticatedMember(self):
        member = self.membership.getAuthenticatedMember()
        self.assertEqual(member.getUserName(), default_user)

    def testGetAuthenticatedMemberIsWrapped(self):
        member = self.membership.getAuthenticatedMember()
        self.assertEqual(member.getUserName(), default_user)
        self.assertEqual(member.__class__.__name__, 'MemberData')
        self.assertEqual(member.aq_parent.__class__.__name__, 'GRUFUser')

    def testGetAuthenticatedMemberIfAnonymous(self):
        self.logout()
        member = self.membership.getAuthenticatedMember()
        self.assertEqual(member.getUserName(), 'Anonymous User')

    def testAnonymousMemberIsNotWrapped(self):
        # Also see http://plone.org/collector/1851
        self.logout()
        member = self.membership.getAuthenticatedMember()
        self.failIfEqual(member.__class__.__name__, 'MemberData')
        self.assertEqual(member.__class__.__name__, 'SpecialUser')

    def testIsAnonymousUser(self):
        self.failIf(self.membership.isAnonymousUser())
        self.logout()
        self.failUnless(self.membership.isAnonymousUser())

    def testWrapUserWrapsBareUser(self):
        user = self.portal.acl_users.getUserById(default_user)
        # XXX: GRUF users are wrapped
        self.failUnless(hasattr(user, 'aq_base'))
        user = aq_base(user)
        user = self.membership.wrapUser(user)
        self.assertEqual(user.__class__.__name__, 'MemberData')
        self.assertEqual(user.aq_parent.__class__.__name__, 'GRUFUser')
        self.assertEqual(user.aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')

    def testWrapUserWrapsWrappedUser(self):
        user = self.portal.acl_users.getUserById(default_user)
        # XXX: GRUF users are wrapped
        self.failUnless(hasattr(user, 'aq_base'))
        user = self.membership.wrapUser(user)
        self.assertEqual(user.__class__.__name__, 'MemberData')
        self.assertEqual(user.aq_parent.__class__.__name__, 'GRUFUser')
        self.assertEqual(user.aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')

    def testWrapUserDoesntWrapMemberData(self):
        user = self.portal.acl_users.getUserById(default_user)
        user.getMemberId = lambda x: 1
        user = self.membership.wrapUser(user)
        self.assertEqual(user.__class__.__name__, 'GRUFUser')

    def testWrapUserDoesntWrapAnonymous(self):
        user = self.membership.wrapUser(nobody)
        self.assertEqual(user.__class__.__name__, 'SpecialUser')

    def testWrapUserWrapsAnonymous(self):
        self.failIf(hasattr(nobody, 'aq_base'))
        user = self.membership.wrapUser(nobody, wrap_anon=1)
        self.assertEqual(user.__class__.__name__, 'MemberData')
        self.assertEqual(user.aq_parent.__class__.__name__, 'SpecialUser')
        self.assertEqual(user.aq_parent.aq_parent.__class__.__name__, 'GroupUserFolder')

    def testGetCandidateLocalRoles(self):
        self.assertEqual(self.membership.getCandidateLocalRoles(self.folder), ('Owner',))
        self.setRoles(['Member', 'Reviewer'])
        self.assertEqual(self.membership.getCandidateLocalRoles(self.folder), ('Owner', 'Reviewer'))

    def testSetLocalRoles(self):
        self.failUnless('Owner' in self.folder.get_local_roles_for_userid(default_user))
        self.setRoles(['Member', 'Reviewer'])
        self.membership.setLocalRoles(self.folder, [default_user, 'user2'], 'Reviewer')
        self.assertEqual(self.folder.get_local_roles_for_userid(default_user), ('Owner', 'Reviewer'))
        self.assertEqual(self.folder.get_local_roles_for_userid('user2'), ('Reviewer',))

    def testDeleteLocalRoles(self):
        self.setRoles(['Member', 'Reviewer'])
        self.membership.setLocalRoles(self.folder, ['user2'], 'Reviewer')
        self.assertEqual(self.folder.get_local_roles_for_userid('user2'), ('Reviewer',))
        self.membership.deleteLocalRoles(self.folder, ['user2'])
        self.assertEqual(self.folder.get_local_roles_for_userid('user2'), ())

    def testGetHomeFolder(self):
        self.failIfEqual(self.membership.getHomeFolder(), None)
        self.assertEqual(self.membership.getHomeFolder('user2'), None)

    def testGetHomeUrl(self):
        self.failIfEqual(self.membership.getHomeUrl(), None)
        self.assertEqual(self.membership.getHomeUrl('user2'), None)

    def testGetAuthenticatedMemberInfo(self):
        member = self.membership.getAuthenticatedMember()
        member.setMemberProperties({'fullname': 'Test user'})
        info = self.membership.getMemberInfo()
        self.assertEqual(info['fullname'], 'Test user')

    def testGetMemberInfo(self):
        self.membership.addMember('user2', 'secret', ['Member'], [],
                                  properties={'fullname': 'Second user'})
        info = self.membership.getMemberInfo('user2')
        self.assertEqual(info['fullname'], 'Second user')

    def testGetCandidateLocalRolesIncludesLocalRolesOnObjectForManager(self):
        self.folder._addRole('my_test_role')
        self.folder.manage_setLocalRoles(default_user, ('Manager','Owner'))
        roles = self.membership.getCandidateLocalRoles(self.folder)
        self.failUnless('my_test_role' in roles,
                        'my_test_role not in: %s'%str(roles))

    def testGetCandidateLocalRolesIncludesLocalRolesOnObjectForAssignees(self):
        self.folder._addRole('my_test_role')
        self.folder.manage_setLocalRoles(default_user, ('my_test_role','Owner'))
        roles = self.membership.getCandidateLocalRoles(self.folder)
        self.failUnless('Owner' in roles)
        self.failUnless('my_test_role' in roles)
        self.assertEqual(len(roles), 2)

    def testGetCandidateLocalRolesForManager(self):
        self.folder._addRole('my_test_role')
        self.folder.manage_setLocalRoles(default_user, ('Manager','Owner'))
        roles = self.membership.getCandidateLocalRoles(self.folder)
        self.failUnless('Manager' in roles)
        self.failUnless('Owner' in roles)
        self.failUnless('Reviewer' in roles)

    def testGetCandidateLocalRolesForOwner(self):
        self.folder._addRole('my_test_role')
        roles = self.membership.getCandidateLocalRoles(self.folder)
        self.failUnless('Owner' in roles)
        self.assertEqual(len(roles), 1)

    def testGetCandidateLocalRolesForAssigned(self):
        self.folder._addRole('my_test_role')
        self.folder.manage_setLocalRoles(default_user, ('Reviewer','Owner'))
        roles = self.membership.getCandidateLocalRoles(self.folder)
        self.failUnless('Owner' in roles)
        self.failUnless('Reviewer' in roles)
        self.assertEqual(len(roles), 2)

    def test_bug4333_delete_user_remove_memberdata(self):
        # delete user should delete portal_memberdata
        memberdata = self.portal.portal_memberdata
        self.setRoles(['Manager'])
        self.addMember('barney', 'Barney Rubble', 'barney@bedrock.com', ['Member'], '2002-01-01')
        barney = self.membership.getMemberById('barney')
        self.failUnlessEqual(barney.email, 'barney@bedrock.com')
        del barney

        self.membership.deleteMembers(['barney'])
        md = memberdata._members
        self.failIf(md.has_key('barney'))

        # There is an _v_ variable that is killed at the end of each request
        # which stores a temporary version of the member object, this is
        # a problem in this test.  In fact, this test does not really
        # demonstrate the bug, which is actually caused by the script not
        # using the tool.
        memberdata._v_temps = None

        self.membership.addMember('barney', 'secret', ['Members'], [])
        barney = self.membership.getMemberById('barney')
        self.failIfEqual(barney.fullname, 'Barney Rubble')
        self.failIfEqual(barney.email, 'barney@bedrock.com')

class TestCreateMemberarea(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('user2', 'secret', ['Member'], [])

    def testCreateMemberarea(self):
        # Should create a memberarea for user2
        members = self.membership.getMembersFolder()
        self.membership.createMemberarea('user2')
        memberfolder = self.membership.getHomeFolder('user2')
        self.failUnless(memberfolder, 'createMemberarea failed to create memberarea')
        # member area creation should be on by default
        self.failUnless(self.membership.getMemberareaCreationFlag())

##     def testWrapUserCreatesMemberarea(self):
##         # This test serves to trip us up should this ever change
##         # Also see http://plone.org/collector/1697
##         members = self.membership.getMembersFolder()
##         user = self.portal.acl_users.getUserById('user2')
##         self.membership.memberareaCreationFlag = 1
##         import pdb; pdb.set_trace()
##         self.membership.wrapUser(user)
##         memberfolder = self.membership.getHomeFolder('user2')
##         self.failUnless(memberfolder, 'wrapUser failed to create memberarea')

    def testCreatMemberareaUsesCurrentUser(self):
        # Should create a memberarea for user2
        self.login('user2')
        self.membership.createMemberarea()
        memberfolder = self.membership.getHomeFolder('user2')
        self.failUnless(memberfolder, 'createMemberarea failed to create memberarea for current user')

    def testNoMemberareaIfNoMembersFolder(self):
        # Should not create a memberarea if the Members folder is missing
        self.portal._delObject('Members')
        self.membership.createMemberarea('user2')
        memberfolder = self.membership.getHomeFolder('user2')
        self.failIf(memberfolder, 'createMemberarea unexpectedly created a memberarea')

    def testNoMemberareaIfMemberareaExists(self):
        # Should not attempt to create a memberarea if a memberarea already exists
        self.membership.createMemberarea('user2')
        # The second call should do nothing (not cause an error)
        self.membership.createMemberarea('user2')

    def testNotifyScriptIsCalled(self):
        # The notify script should be called
        self.portal.notifyMemberAreaCreated = dummy.Raiser(dummy.Error)
        self.assertRaises(dummy.Error, self.membership.createMemberarea, 'user2')

    def testCreateMemberareaAlternateName(self):
        # Alternate method name 'createMemberaArea' should work
        members = self.membership.getMembersFolder()
        self.membership.createMemberArea('user2')
        memberfolder = self.membership.getHomeFolder('user2')
        self.failUnless(memberfolder, 'createMemberArea failed to create memberarea')

    def testCreateMemberareaLPF(self):
        # Should create a Large Plone Folder instead of a normal Folder
        self.membership.setMemberAreaType('Large Plone Folder')
        self.membership.createMemberarea('user2')
        memberfolder = self.membership.getHomeFolder('user2')
        self.assertEqual(memberfolder.getPortalTypeName(), 'Large Plone Folder')

    def testCreateMemberareaWhenDisabled(self):
        # Should not create a member area
        self.membership.setMemberareaCreationFlag()
        self.failIf(self.membership.getMemberareaCreationFlag())
        self.membership.createMemberarea('user2')
        memberfolder = self.membership.getHomeFolder('user2')
        self.failIf(memberfolder, 'createMemberarea created memberarea despite flag')


class TestMemberareaSetup(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('user2', 'secret', ['Member'], [])
        self.membership.createMemberarea('user2')
        self.home = self.membership.getHomeFolder('user2')

    def testMemberareaIsPloneFolder(self):
        # Memberarea should be a Plone folder
        self.assertEqual(self.home.meta_type, 'ATFolder')
        self.assertEqual(self.home.portal_type, 'Folder')

    def testMemberareaIsOwnedByMember(self):
        # Memberarea should be owned by member
        try: owner_info = self.home.getOwnerTuple()
        except AttributeError:
            owner_info = self.home.getOwner(info=1)
        self.assertEqual(owner_info[0], [PloneTestCase.portal_name, 'acl_users'])
        self.assertEqual(owner_info[1], 'user2')
        self.assertEqual(len(self.home.get_local_roles()), 1)
        self.assertEqual(self.home.get_local_roles_for_userid('user2'), ('Owner',))

    def testMemberareaHasDescription(self):
        # Memberarea should have a description
        self.failUnless(self.home.Description())

    def testMemberareaIsCataloged(self):
        # Memberarea should be cataloged
        catalog = self.portal.portal_catalog
        self.failUnless(catalog(id='user2', Type='Folder', Title="user2's Home"),
                        "Could not find user2's home folder in the catalog")

    def testHomePageNotExists(self):
        # Should not have an index_html document anymore
        self.failIf('index_html' in self.home.objectIds())


class TestSearchForMembers(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.memberdata = self.portal.portal_memberdata
        self.membership = self.portal.portal_membership
        # Don't let default_user disturb results
        self.portal.acl_users._doDelUsers([default_user])
        # Add some members
        self.addMember('fred', 'Fred Flintstone',
                       'fred@bedrock.com', ['Member', 'Reviewer'],
                       '2002-01-01')
        self.addMember('barney', 'Barney Rubble',
                       'barney@bedrock.com', ['Member'],
                       '2002-01-01')
        self.addMember('brubble', 'Bambam Rubble',
                       'bambam@bambam.net', ['Member'],
                       '2003-12-31')
        # MUST reset this
        self.memberdata._v_temps = None

    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})

    def testSearchById(self):
        # Should search id and fullname
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='brubble')), 1)
        self.assertEqual(len(search(name='barney')), 1)
        self.assertEqual(len(search(name='rubble')), 2)

    def testSearchByName(self):
        # Should search id and fullname
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='rubble')), 2)
        self.assertEqual(len(search(name='stone')), 1)

    def testSearchByEmail(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(email='bedrock')), 2)
        self.assertEqual(len(search(email='bambam')), 1)

    def testSearchByRoles(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(roles=['Member'])), 3)
        self.assertEqual(len(search(roles=['Reviewer'])), 1)

    def testSearchByLastLoginTime(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(last_login_time=DateTime('2002-01-01'))), 3)
        self.assertEqual(len(search(last_login_time=DateTime('2003-01-01'))), 1)

    def testSearchLoginBeforeSpecifiedTime(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(last_login_time=DateTime('2002-01-02'),
                                    before_specified_time=True)), 2)
        self.assertEqual(len(search(last_login_time=DateTime('2004-01-01'),
                                    before_specified_time=True)), 3)

    def testSearchByNameAndEmail(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='rubble', email='bedrock')), 1)
        self.assertEqual(len(search(name='bambam', email='bedrock')), 0)

    def testSearchByNameAndRoles(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='fred', roles=['Reviewer'])), 1)
        self.assertEqual(len(search(name='fred', roles=['Manager'])), 0)

    def testSearchByNameAndLastLoginTime(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='rubble', last_login_time=DateTime('2002-01-01'))), 2)
        self.assertEqual(len(search(name='flintstone', last_login_time=DateTime('2003-01-01'))), 0)

    def testSearchByNameAndLoginBeforeSpecifiedTime(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='rubble',
                                    last_login_time=DateTime('2002-01-01'),
                                    before_specified_time=True)), 0)
        self.assertEqual(len(search(name='rubble',
                                    last_login_time=DateTime('2002-01-02'),
                                    before_specified_time=True)), 1)
        self.assertEqual(len(search(name='flintstone',
                                    last_login_time=DateTime('2003-01-01'),
                                    before_specified_time=True)), 1)

    def testSearchByEmailAndRoles(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(email='fred', roles=['Reviewer'])), 1)
        self.assertEqual(len(search(email='fred', roles=['Manager'])), 0)

    def testSearchByEmailAndLastLoginTime(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(email='bedrock', last_login_time=DateTime('2002-01-01'))), 2)
        self.assertEqual(len(search(email='bedrock', last_login_time=DateTime('2003-01-01'))), 0)

    def testSearchByEmailAndLoginBeforeSpecifiedTime(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(email='bedrock',
                                    last_login_time=DateTime('2002-01-01'),
                                    before_specified_time=True)), 0)
        self.assertEqual(len(search(email='bedrock',
                                    last_login_time=DateTime('2003-01-01'),
                                    before_specified_time=True)), 2)

    def testSearchByRolesAndLastLoginTime(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(roles=['Member'], last_login_time=DateTime('2002-01-01'))), 3)
        self.assertEqual(len(search(roles=['Reviewer'], last_login_time=DateTime('2002-01-01'))), 1)
        self.assertEqual(len(search(roles=['Member'], last_login_time=DateTime('2003-01-01'))), 1)

    def testSearchByRolesAndLoginBeforeSpecifiedTime(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(roles=['Member'],
                                    last_login_time=DateTime('2002-01-01'),
                                    before_specified_time=True)), 0)
        self.assertEqual(len(search(roles=['Member'],
                                    last_login_time=DateTime('2003-01-01'),
                                    before_specified_time=True)), 2)
        self.assertEqual(len(search(roles=['Member'],
                                    last_login_time=DateTime('2004-01-01'),
                                    before_specified_time=True)), 3)
        self.assertEqual(len(search(roles=['Reviewer'],
                                    last_login_time=DateTime('2002-01-01'),
                                    before_specified_time=True)), 0)
        self.assertEqual(len(search(roles=['Reviewer'],
                                    last_login_time=DateTime('2004-01-01'),
                                    before_specified_time=True)), 1)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMembershipTool))
    suite.addTest(makeSuite(TestCreateMemberarea))
    suite.addTest(makeSuite(TestMemberareaSetup))
    suite.addTest(makeSuite(TestSearchForMembers))
    return suite

if __name__ == '__main__':
    framework()
