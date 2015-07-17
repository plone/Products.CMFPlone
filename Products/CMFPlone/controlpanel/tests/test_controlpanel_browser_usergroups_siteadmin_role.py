# -*- coding: utf-8 -*-
"""This test has been moved over to CMFPlone from plone.app.controlpanel.
   It has been cleaned up a bit. Though, it still is kind of messy because it
   comes with its own test fixture. Would be nice to refactor that to use the
   CMFPlone fixture at some point.
"""
from cStringIO import StringIO
from urllib import urlencode
from plone.protect.authenticator import createToken

import re
import transaction

from plone.app.testing.bbb import PloneTestCase as FunctionalTestCase
from plone.app.testing.bbb import PloneTestCaseFixture
from plone.app import testing
from Products.CMFCore.utils import getToolByName


class ControlPanelFixture(PloneTestCaseFixture):

    def setUpPloneSite(self, portal):
        super(ControlPanelFixture, self).setUpPloneSite(portal)
        portal.acl_users.userFolderAddUser('root', 'secret', ['Manager'], [])


CP_FIXTURE = ControlPanelFixture()
CP_FUNCTIONAL_LAYER = testing.FunctionalTesting(
    bases=(CP_FIXTURE,), name='ControlPanel:Functional')


class UserGroupsControlPanelTestCase(FunctionalTestCase):
    """user/groups-specific test case"""

    layer = CP_FUNCTIONAL_LAYER

    def afterSetUp(self):
        super(UserGroupsControlPanelTestCase, self).afterSetUp()
        members = [
            {
              'username': 'DIispfuF',
              'fullname': 'Kevin Hughes',
              'email': 'DIispfuF@example.com'
            },
        ]
        regtool = getToolByName(self.portal, 'portal_registration')
        for member in members:
            regtool.addMember(
                member['username'],
                'somepassword',
                properties=member
            )
        transaction.commit()


class TestSiteAdministratorRoleFunctional(UserGroupsControlPanelTestCase):

    def _getauth(self, userName):
        self.login(userName)
        return createToken()

    def _simplify_white_space(self, text):
        """For easier testing we replace all white space with one space.

        And we remove white space around '<' and '>'.

        So this:

          <p
              id="foo"> Bar
          </p>

        becomes this:

          <p id="foo">Bar</p>
        """
        text = re.sub('\s*<\s*', '<', text)
        text = re.sub('\s*>\s*', '>', text)
        text = re.sub('\s+', ' ', text)
        return text

    def afterSetUp(self):
        super(TestSiteAdministratorRoleFunctional, self).afterSetUp()

        # add a user with the Site Administrator role
        self.portal.portal_membership.addMember(
            'siteadmin',
            'secret',
            ['Site Administrator'],
            []
        )

        self.manager_token = self._getauth('root')
        self.siteadmin_token = self._getauth('siteadmin')

        self.normal_user = 'DIispfuF'

    def testControlPanelOverview(self):
        # make sure we can view the Site Setup page,
        # at both old and new URLs
        res = self.publish('/plone/plone_control_panel', 'siteadmin:secret')
        self.assertEqual(200, res.status)
        res = self.publish(
            '/plone/@@overview-controlpanel', 'siteadmin:secret'
        )
        self.assertEqual(200, res.status)

    def testUserManagerRoleCheckboxIsDisabledForNonManagers(self):
        res = self.publish(
            '/plone/@@usergroup-userprefs', basic='siteadmin:secret'
        )
        contents = res.getOutput()
        self.assertTrue('<input type="checkbox" class="noborder" '
                        'name="users.roles:list:records" value="Manager" '
                        'disabled="disabled" />' in contents)

    def testManagerCanDelegateManagerRoleForUsers(self):
        # a user with the Manager role can grant the Manager role
        form = {
            '_authenticator': self.manager_token,
            'users.id:records': self.normal_user,
            'users.roles:list:records': 'Manager',
            'form.button.Modify': 'Save',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish('/plone/@@usergroup-userprefs',
                           request_method='POST', stdin=post_data,
                           basic='root:secret')
        self.assertEqual(200, res.status)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Manager', 'Authenticated'], roles)

    def testNonManagersCannotDelegateManagerRoleForUsers(self):
        # a user without the Manager role cannot delegate the Manager role
        form = {
            '_authenticator': self.siteadmin_token,
            'users.id:records': self.normal_user,
            'users.roles:list:records': 'Manager',
            'form.button.Modify': 'Save',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish('/plone/@@usergroup-userprefs',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Member', 'Authenticated'], roles)

    def testNonManagersCanEditOtherRolesOfUsersWithManagerRole(self):
        roles = self.portal.acl_users.getUserById('root').getRoles()
        self.assertEqual(['Manager', 'Authenticated'], roles)
        form = {
            '_authenticator': self.siteadmin_token,
            'users.id:records': 'root',
            'users.roles:list:records': ('Member', 'Manager'),
            'form.button.Modify': 'Save',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form, doseq=True))
        res = self.publish('/plone/@@usergroup-userprefs',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(200, res.status)
        roles = self.portal.acl_users.getUserById('root').getRoles()
        self.assertEqual(['Member', 'Manager', 'Authenticated'], roles)

    def testGroupManagerRoleCheckboxIsDisabledForNonManagers(self):
        res = self.publish(
            '/plone/@@usergroup-groupprefs',
            basic='siteadmin:secret'
        )
        contents = self._simplify_white_space(res.getOutput())
        self.assertTrue('<input type="checkbox" class="noborder" '
                        'name="group_Reviewers:list" value="Manager" '
                        'disabled="disabled" />' in contents)

    def testManagerCanDelegateManagerRoleForGroups(self):
        # a user with the Manager role can grant the Manager role
        form = {
            '_authenticator': self.manager_token,
            'group_Reviewers:list': ('', 'Manager'),
            'form.button.Modify': 'Save',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form, doseq=True))
        res = self.publish('/plone/@@usergroup-groupprefs',
                           request_method='POST', stdin=post_data,
                           basic='root:secret')
        self.assertEqual(200, res.status)
        roles = self.portal.acl_users.getGroupById('Reviewers').getRoles()
        self.assertEqual(['Manager', 'Authenticated'], roles)

    def testNonManagersCannotDelegateManagerRoleForGroups(self):
        # a user without the Manager role cannot delegate the Manager role
        form = {
            '_authenticator': self.siteadmin_token,
            'group_Reviewers:list': ('', 'Manager'),
            'form.button.Modify': 'Save',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form, doseq=True))
        res = self.publish('/plone/@@usergroup-groupprefs',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getGroupById('Reviewers').getRoles()
        self.assertEqual(['Reviewer', 'Authenticated'], roles)

    def testNonManagersCanEditOtherRolesOfGroupsWithManagerRole(self):
        roles = self.portal.acl_users.getUserById('root').getRoles()
        self.assertEqual(['Manager', 'Authenticated'], roles)
        form = {
            '_authenticator': self.siteadmin_token,
            'group_Administrators:list': ('', 'Member', 'Manager'),
            'form.button.Modify': 'Save',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form, doseq=True))
        res = self.publish('/plone/@@usergroup-groupprefs',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(200, res.status)
        roles = self.portal.acl_users.getGroupById('Administrators').getRoles()
        self.assertEqual(['Member', 'Manager', 'Authenticated'], roles)

    def test_usergroup_usermembership_blocks_escalation(self):
        # groups granting the Manager role shouldn't show as a valid option to
        # add
        res = self.publish(
            '/plone/@@usergroup-usermembership?userid=%s' % self.normal_user,
            basic='siteadmin:secret'
        )
        contents = self._simplify_white_space(res.getOutput())
        self.assertTrue(
            '<input type="checkbox" class="noborder" name="add:list" '
            'value="Administrators" disabled="disabled" />' in contents
        )

        # and should not be addable
        form = {
            '_authenticator': self.siteadmin_token,
            'add:list': 'Administrators',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish(
            '/plone/@@usergroup-usermembership?userid=%s' % self.normal_user,
            request_method='POST', stdin=post_data,
            basic='siteadmin:secret'
        )
        self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Member', 'Authenticated'], roles)

    def test_usergroup_groupmembership_blocks_escalation(self):
        # should not show section to add users for groups granting the Manager
        # role
        res = self.publish(
            '/plone/@@usergroup-groupmembership?groupname=Administrators',
            basic='siteadmin:secret'
        )
        contents = self._simplify_white_space(res.getOutput())
        self.assertFalse('Search for new group members' in contents)

        # and should not be addable if we try to force it
        form = {
            '_authenticator': self.siteadmin_token,
            'add:list': self.normal_user,
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish(
            '/plone/@@usergroup-groupmembership?groupname=Administrators',
            request_method='POST', stdin=post_data,
            basic='siteadmin:secret'
        )
        self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Member', 'Authenticated'], roles)

    def test_user_registration_form_blocks_escalation(self):
        # groups granting the Manager role should not be available for
        # selection
        res = self.publish('/plone/@@new-user', basic='siteadmin:secret')
        contents = self._simplify_white_space(res.getOutput())
        self.assertFalse(
            '<input class="label checkboxType" id="form.groups.0" '
            'name="form.groups" type="checkbox" value="Administrators '
            '(Administrators)" />' in contents
        )

        # and should not be addable if we try to force it
        form = {
            '_authenticator': self.siteadmin_token,
            'form.widgets.username': 'newuser',
            'form.widgets.email': 'newuser@example.com',
            'form.widgets.password': 'secret',
            'form.widgets.password_ctl': 'secret',
            'form.widgets.groups:list': 'Administrators',
            'form.widgets.groups-empty-marker': '1',
            'form.buttons.register': 'Register',
            }
        post_data = StringIO(urlencode(form))
        res = self.publish('/plone/@@new-user',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertNotEqual(200, res.status)
        self.assertEqual(None, self.portal.acl_users.getUserById('newuser'))

    def test_users_overview_blocks_deleting_managers(self):
        # a user without the Manager role cannot delete a user with the
        # Manager role
        res = self.publish('/plone/@@usergroup-userprefs', basic='siteadmin:secret')
        contents = self._simplify_white_space(res.getOutput())
        self.assertTrue('<input type="checkbox" class="noborder notify" '
                        'name="delete:list" value="root" disabled="disabled" />'
                        in contents)

        form = {
            '_authenticator': self.siteadmin_token,
            'users.id:records': 'root',
            'delete:list': 'root',
            'form.button.Modify': 'Save',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish('/plone/@@usergroup-userprefs',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(403, res.status)
        user = self.portal.acl_users.getUserById('root')
        self.assertTrue(user is not None)

    def test_groups_overview_blocks_deleting_managers(self):
        # a user without the Manager role cannot delete a group with the
        # Manager role
        res = self.publish(
            '/plone/@@usergroup-groupprefs',
            basic='siteadmin:secret'
        )
        contents = self._simplify_white_space(res.getOutput())
        self.assertTrue(
            '<input type="checkbox" class="noborder notify" '
            'name="delete:list" value="Administrators" disabled="disabled" />'
            in contents
        )

        form = {
            '_authenticator': self.siteadmin_token,
            'delete:list': 'Administrators',
            'form.button.Modify': 'Save',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish('/plone/@@usergroup-groupprefs',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(403, res.status)
        group = self.portal.acl_users.getGroupById('Administrators')
        self.assertTrue(group is not None)
