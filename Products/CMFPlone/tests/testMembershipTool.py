#
# MembershipTool tests
#

import os
from cStringIO import StringIO

from OFS.Image import Image

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy
from Products.CMFCore.tests.base.testcase import WarningInterceptor

from AccessControl.User import nobody
from AccessControl import Unauthorized
from Acquisition import aq_base
from DateTime import DateTime
from zExceptions import BadRequest

default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password


class TestMembershipTool(PloneTestCase.PloneTestCase, WarningInterceptor):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.groups = self.portal.portal_groups
        self._trap_warning_output()

    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})
    def makeRealImage(self):
        import Products.CMFPlone as plone
        plone_path = os.path.dirname(plone.__file__)
        path = os.path.join(plone_path, 'tests', 'images', 'test.jpg')
        image = open(path, 'rb')
        image_upload = dummy.FileUpload(dummy.FieldStorage(image))
        return image_upload

    def testNoMorePersonalFolder(self):
        # .personal folders are history
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
        # first we need a valid image
        image = self.makeRealImage()
        self.membership.changeMemberPortrait(image, default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).meta_type, 'Image')

    def testDeletePersonalPortrait(self):
        # Should delete the portrait image
        image = self.makeRealImage()
        self.membership.changeMemberPortrait(image, default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), default_user)
        self.membership.deletePersonalPortrait(default_user)
        self.assertEqual(self.membership.getPersonalPortrait(default_user).getId(), 'defaultUser.gif')

    def testGetPersonalPortraitWithoutPassingId(self):
        # Should return the logged in users portrait if no id is given
        image = self.makeRealImage()
        self.membership.changeMemberPortrait(image, default_user)
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
        self.groups.addGroup('Foo')
        self.groups.addGroup('Bar')
        self.assertEqual(len(uf.getUserNames()), 1)
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
        self.groups.addGroup('Foo')
        self.groups.addGroup('Bar')
        self.assertEqual(len(uf.getUserNames()), 1)
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
        groups = self.groups
        groups.addGroup(group2, None, [], [])
        group = groups.getGroupById(group2)
        self.loginAsPortalOwner() # GRUF 3.52
        group.addMember(default_user)
        self.login(default_user) # Back to normal
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
        self.assertEqual(member.aq_parent.__class__.__name__, 'PloneUser')

    def testGetAuthenticatedMember(self):
        member = self.membership.getAuthenticatedMember()
        self.assertEqual(member.getUserName(), default_user)

    def testGetAuthenticatedMemberIsWrapped(self):
        member = self.membership.getAuthenticatedMember()
        self.assertEqual(member.getUserName(), default_user)
        self.assertEqual(member.__class__.__name__, 'MemberData')
        self.assertEqual(member.aq_parent.__class__.__name__, 'PloneUser')

    def testGetAuthenticatedMemberIfAnonymous(self):
        self.logout()
        member = self.membership.getAuthenticatedMember()
        self.assertEqual(member.getUserName(), 'Anonymous User')

    def testAnonymousMemberIsNotWrapped(self):
        # Also see http://dev.plone.org/plone/ticket/1851
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
        # TODO: GRUF users are wrapped
        self.failUnless(hasattr(user, 'aq_base'))
        user = aq_base(user)
        user = self.membership.wrapUser(user)
        self.assertEqual(user.__class__.__name__, 'MemberData')
        self.assertEqual(user.aq_parent.__class__.__name__, 'PloneUser')
        self.assertEqual(user.aq_parent.aq_parent.__class__.__name__, 'PluggableAuthService')

    def testWrapUserWrapsWrappedUser(self):
        user = self.portal.acl_users.getUserById(default_user)
        # TODO: GRUF users are wrapped
        self.failUnless(hasattr(user, 'aq_base'))
        user = self.membership.wrapUser(user)
        self.assertEqual(user.__class__.__name__, 'MemberData')
        self.assertEqual(user.aq_parent.__class__.__name__, 'PloneUser')
        self.assertEqual(user.aq_parent.aq_parent.__class__.__name__, 'PluggableAuthService')

    def testWrapUserDoesntWrapMemberData(self):
        user = self.portal.acl_users.getUserById(default_user)
        user.getMemberId = lambda x: 1
        user = self.membership.wrapUser(user)
        self.assertEqual(user.__class__.__name__, 'PloneUser')

    def testWrapUserDoesntWrapAnonymous(self):
        user = self.membership.wrapUser(nobody)
        self.assertEqual(user.__class__.__name__, 'SpecialUser')

    def testWrapUserWrapsAnonymous(self):
        self.failIf(hasattr(nobody, 'aq_base'))
        user = self.membership.wrapUser(nobody, wrap_anon=1)
        self.assertEqual(user.__class__.__name__, 'MemberData')
        self.assertEqual(user.aq_parent.__class__.__name__, 'SpecialUser')
        self.assertEqual(user.aq_parent.aq_parent.__class__.__name__, 'PluggableAuthService')

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
        self.failUnlessEqual(barney.getProperty('email'), 'barney@bedrock.com')
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

        self.membership.addMember('barney', 'secret', ['Member'], [])
        barney = self.membership.getMemberById('barney')
        self.failIfEqual(barney.getProperty('fullname'), 'Barney Rubble')
        self.failIfEqual(barney.getProperty('email'), 'barney@bedrock.com')

    def testBogusMemberPortrait(self):
        # Should change the portrait image
        bad_file = dummy.File(data='<div>This is a lie!!!</div>',
                              headers={'content_type':'image/jpeg'})
        self.assertRaises(IOError, self.membership.changeMemberPortrait,
                          bad_file, default_user)

    def testGetBadMembers(self):
        # Should list members with bad images
        # We should not have any bad images out of the box
        self.assertEqual(self.membership.getBadMembers(), [])
        # Let's add one
        bad_file = Image(id=default_user, title='',
                               file=StringIO('<div>This is a lie!!!</div>'))
        # Manually set a bad image using private methods
        self.portal.portal_memberdata._setPortrait(bad_file, default_user)
        self.assertEqual(self.membership.getBadMembers(), [default_user])
        # Try an empty image
        empty_file =  Image(id=default_user, title='', file=StringIO(''))
        self.portal.portal_memberdata._setPortrait(empty_file, default_user)
        self.assertEqual(self.membership.getBadMembers(), [])
        # And a good image
        self.membership.changeMemberPortrait(self.makeRealImage(), default_user)
        self.assertEqual(self.membership.getBadMembers(), [])

    def beforeTearDown(self):
        self._free_warning_output()


class TestCreateMemberarea(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.addMember('user2', 'secret', ['Member'], [])

    def testCreateMemberarea(self):
        # Should create a memberarea for user2
        if self.membership.memberareaCreationFlag == True:
            members = self.membership.getMembersFolder()
            self.membership.createMemberarea('user2')
            memberfolder = self.membership.getHomeFolder('user2')
            self.failUnless(memberfolder, 'createMemberarea failed to create memberarea')
            # member area creation should be on by default
            self.failUnless(self.membership.getMemberareaCreationFlag())

    def testCreatMemberareaUsesCurrentUser(self):
        if self.membership.memberareaCreationFlag == True:
            # Should create a memberarea for user2
            self.login('user2')
            self.membership.createMemberarea()
            memberfolder = self.membership.getHomeFolder('user2')
            self.failUnless(memberfolder, 'createMemberarea failed to create memberarea for current user')
        else:
            pass

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
        if self.membership.memberareaCreationFlag == True:
            self.portal.notifyMemberAreaCreated = dummy.Raiser(dummy.Error)
            self.assertRaises(dummy.Error, self.membership.createMemberarea, 'user2')       

    def testCreateMemberareaAlternateName(self):
        # Alternate method name 'createMemberaArea' should work
        if self.membership.memberareaCreationFlag == True:
            members = self.membership.getMembersFolder()
            self.membership.createMemberArea('user2')
            memberfolder = self.membership.getHomeFolder('user2')
            self.failUnless(memberfolder, 'createMemberArea failed to create memberarea')

    def testCreateMemberareaLPF(self):
        # Should create a Large Plone Folder instead of a normal Folder
        if self.membership.memberareaCreationFlag == True:
            self.membership.setMemberAreaType('Large Plone Folder')
            self.membership.createMemberarea('user2')
            memberfolder = self.membership.getHomeFolder('user2')
            self.assertEqual(memberfolder.getPortalTypeName(), 'Large Plone Folder')

    def testCreateMemberareaWhenDisabled(self):
        # Should not create a member area
        self.membership.setMemberareaCreationFlag = False
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
        if self.membership.memberareaCreationFlag == True:
            # Memberarea should be a Plone folder
            self.assertEqual(self.home.meta_type, 'ATFolder')
            self.assertEqual(self.home.portal_type, 'Folder')

    def testMemberareaIsOwnedByMember(self):
        if self.membership.memberareaCreationFlag == True:
            # Memberarea should be owned by member
            try: owner_info = self.home.getOwnerTuple()
            except AttributeError:
                owner_info = self.home.getOwner(info=1)
            self.assertEqual(owner_info[0], [PloneTestCase.portal_name, 'acl_users'])
            self.assertEqual(owner_info[1], 'user2')
            self.assertEqual(len(self.home.get_local_roles()), 1)
            self.assertEqual(self.home.get_local_roles_for_userid('user2'), ('Owner',))

    def testMemberareaHasDescription(self):
        # Memberarea should have a description - not in 2.1 ~limi
        #self.failUnless(self.home.Description())
        pass

    def testMemberareaIsCataloged(self):
        if self.membership.memberareaCreationFlag == True:
            # Memberarea should be cataloged
            catalog = self.portal.portal_catalog
            self.failUnless(catalog(id='user2', Type='Folder', Title="user2"),
                            "Could not find user2's home folder in the catalog")

    def testHomePageNotExists(self):
        if self.membership.memberareaCreationFlag == True:
            # Should not have an index_html document anymore
            self.failIf('index_html' in self.home.objectIds())


class TestSearchForMembers(PloneTestCase.PloneTestCase, WarningInterceptor):

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
        self._trap_warning_output()


    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})

    def testSearchById(self):
        # Should search id and fullname
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='brubble')), 0)
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


    def testSearchByNameAndEmail(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='rubble', email='bedrock')), 1)
        self.assertEqual(len(search(name='bambam', email='bedrock')), 0)

    def testSearchByNameAndRoles(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(name='fred', roles=['Reviewer'])), 1)
        self.assertEqual(len(search(name='fred', roles=['Manager'])), 0)


    def testSearchByEmailAndRoles(self):
        search = self.membership.searchForMembers
        self.assertEqual(len(search(email='fred', roles=['Reviewer'])), 1)
        self.assertEqual(len(search(email='fred', roles=['Manager'])), 0)

    def beforeTearDown(self):
        self._free_warning_output()


class TestDefaultUserAndPasswordNotChanged(PloneTestCase.PloneTestCase):
    # A test for a silly transaction/persistency bug in PlonePAS

    def afterSetUp(self):
        self.membership = self.portal.portal_membership

    def testDefaultUserAndPasswordUnchanged(self):
        member = self.membership.getAuthenticatedMember()
        self.assertEqual(member.getUserName(), default_user)
        self.failUnless(self.membership.testCurrentPassword(default_password))
        self.failIf(self.membership.testCurrentPassword('geheim'))


class TestMethodProtection(PloneTestCase.PloneTestCase):
    # MembershipTool is missing security declarations
    # http://dev.plone.org/plone/ticket/5432

    _unprotected = (
        'changeMemberPortrait',
        'deletePersonalPortrait',
        'testCurrentPassword',
    )

    def afterSetUp(self):
        self.membership = self.portal.portal_membership

    def assertUnprotected(self, object, method):
        self.logout()
        object.restrictedTraverse(method)

    def assertProtected(self, object, method):
        self.logout()
        self.assertRaises(Unauthorized, object.restrictedTraverse, method)

    for method in _unprotected:
        exec "def testUnprotected_%s(self):" \
             "    self.assertProtected(self.membership, '%s')" % (method, method)

        exec "def testMemberAccessible_%s(self):" \
             "    self.membership.restrictedTraverse('%s')" % (method, method)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMembershipTool))
    suite.addTest(makeSuite(TestCreateMemberarea))
    suite.addTest(makeSuite(TestMemberareaSetup))
    suite.addTest(makeSuite(TestSearchForMembers))
    suite.addTest(makeSuite(TestDefaultUserAndPasswordNotChanged))
    suite.addTest(makeSuite(TestMethodProtection))
    return suite
