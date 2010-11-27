#
# Tests the control panel scripts
#

from Products.CMFPlone.tests import PloneTestCase
from zExceptions import Forbidden
from cStringIO import StringIO

from DateTime import DateTime

default_user = PloneTestCase.default_user
default_password = PloneTestCase.default_password


class TestNoGETControlPanel(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.folder_path = '/'+self.folder.absolute_url(1)
        self.setRoles(['Manager'])
        self.portal.portal_membership.addMember('bribri', 'secret', ['Manager'], [])
        self.login('bribri')

    def _onlyPOST(self, path, qstring='', success=200, rpath=None):
        qstring += '&%s=%s' % self.getAuthenticator()
        basic_auth = '%s:%s' % ('bribri', 'secret')
        env = dict()
        if rpath:
            env['HTTP_REFERER'] = self.app.absolute_url() + rpath
        response = self.publish('%s?%s' % (path, qstring), basic_auth, env,
                                handle_errors=True)
        self.assertEqual(response.getStatus(), 403)

        data = StringIO(qstring)
        if 'QUERY_STRING' in env:
            del env['QUERY_STRING']
        response = self.publish(path, basic_auth, env, request_method='POST',
                                stdin=data)
        self.assertEqual(response.getStatus(), success)

    def test_prefsGroupMemberAdd(self):
        self.groups = self.portal.portal_groups
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        path = self.folder_path + '/prefs_group_members_add'
        qstring = 'groupname=%s&add:list=%s' % ('foo',default_user)
        self._onlyPOST(path, qstring)


    def test_prefsGroupMemberRemove(self):
        self.groups = self.portal.portal_groups
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        group = self.groups.getGroupById('foo')
        group.addMember(default_user)
        path = self.folder_path + '/prefs_group_members_delete'
        qstring = 'groupname=%s&delete:list=%s' % ('foo',default_user)
        self._onlyPOST(path, qstring)

    def test_prefsGroupEdit(self):
        path = self.folder_path + '/prefs_group_edit'
        qstring = 'addname=%s' % 'foo'
        self._onlyPOST(path, qstring, success=302)

    def test_changeOwnership(self):
        path = self.folder_path + '/change_ownership'
        qstring = 'userid=%s' % default_user
        self._onlyPOST(path, qstring, success=302)

    def test_loginChangePassword(self):
        path = self.folder_path + '/login_change_password'
        qstring = 'password=foo'
        self._onlyPOST(path, qstring)

class TestPrefsUserManage(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 0
        self.setupAuthenticator()

    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({'fullname': fullname, 'email': email,
                                    'last_login_time': DateTime(last_login_time),})

    def testPrefsAddGroupPostOnly(self):
        self.setRoles(['Manager'])	
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.portal.prefs_group_edit, addname='foo')

    def testPrefsUserMembershipEditPostOnly(self):
 	self.setRoles(['Manager'])
        self.groups = self.portal.portal_groups
        self.groups.groupWorkspacesCreationFlag = 0
        self.groups.addGroup('foo')
        self.setRequestMethod('GET')
        self.app.REQUEST.set('delete',['foo'])
        self.assertRaises(Forbidden, self.portal.prefs_user_membership_edit, userid='barney')
        del self.app.REQUEST.other['delete']
        self.app.REQUEST.set('add',['foo'])
        self.assertRaises(Forbidden, self.portal.prefs_user_membership_edit, userid='barney')

    def test_ploneChangePasswordPostOnly(self):
        self.login(default_user)
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.portal.plone_change_password, current=default_password, password=default_password, password_confirm=default_password)

    def test_bug4333_delete_user_remove_memberdata(self):
        # delete user should delete portal_memberdata
        memberdata = self.portal.portal_memberdata
        self.setRoles(['Manager'])
        self.addMember('barney', 'Barney Rubble', 'barney@bedrock.com', ['Member'], '2002-01-01')
        barney = self.membership.getMemberById('barney')
        self.failUnlessEqual(barney.getProperty('email'), 'barney@bedrock.com')
        del barney

        self.setRequestMethod('POST')
        self.portal.prefs_user_manage(delete=['barney'])
        self.setRequestMethod('GET')
        md = memberdata._members
        self.failIf('barney' in md)

        # There is an _v_ variable that is killed at the end of each request
        # which stores a temporary version of the member object, this is
        # a problem in this test.
        memberdata._v_temps = None

        self.membership.addMember('barney', 'secret', ['Member'], [])
        barney = self.membership.getMemberById('barney')
        self.failIfEqual(barney.getProperty('fullname'), 'Barney Rubble')
        self.failIfEqual(barney.getProperty('email'), 'barney@bedrock.com')


class TestAccessControlPanelScripts(PloneTestCase.FunctionalTestCase):
    '''Yipee, functional tests'''

    def afterSetUp(self):
        self.portal_path = self.portal.absolute_url(1)
        self.basic_auth = '%s:%s' % (default_user, default_password)

    def testUserInformation(self):
        '''Test access to user details.'''
        self.setRoles(['Manager'])
        response = self.publish('%s/@@user-information?userid=%s' %
                                (self.portal_path, default_user),
                                self.basic_auth)

        self.assertEquals(response.getStatus(), 200)

    def testUserPreferences(self):
        '''Test access to user details.'''
        self.setRoles(['Manager'])
        response = self.publish('%s/@@user-preferences?userid=%s' %
                                (self.portal_path, default_user),
                                self.basic_auth)


        self.assertEquals(response.getStatus(), 200)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPrefsUserManage))
    suite.addTest(makeSuite(TestAccessControlPanelScripts))
    suite.addTest(makeSuite(TestNoGETControlPanel))
    return suite
