from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from urllib.parse import urlencode

import re
import transaction
import unittest
import zExceptions


class TestSiteAdministratorRoleFunctional(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def _generateUsers(self):
        rtool = getToolByName(self.portal, 'portal_registration')
        rtool.addMember('DIispfuF', 'secret', ['Member'], [])
        rtool.addMember('siteadmin', 'secret', ['Site Administrator'], [])
        rtool.addMember('root', 'secret', ['Manager'], [])

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.usergroups_url = "%s/@@usergroup-userprefs" % self.portal_url
        self.groups_url = "%s/@@usergroup-groupprefs" % self.portal_url
        self._generateUsers()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        transaction.commit()

        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            f'Basic {TEST_USER_ID}:{TEST_USER_PASSWORD}'
        )
        self.normal_user = 'DIispfuF'

    def _get_authenticator(self, browser=None):
        if not browser:
            browser = self.browser
        return browser.getControl(name='_authenticator').value

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
        text = re.sub(r'\s*<\s*', '<', text)
        text = re.sub(r'\s*>\s*', '>', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    def testControlPanelOverview(self):
        # make sure we can view the Site Setup page,
        # at both old and new URLs
        self.assertFalse(self.portal.restrictedTraverse('plone_control_panel', False))
        view = self.portal.restrictedTraverse('overview-controlpanel')
        self.assertTrue(view())

    def testUserManagerRoleCheckboxIsDisabledForNonManagers(self):
        login(self.portal, 'siteadmin')
        view = self.portal.restrictedTraverse('@@usergroup-userprefs')
        contents = view()
        self.assertTrue('<input type="checkbox" class="noborder" '
                        'name="users.roles:list:records" value="Manager" '
                        'disabled="disabled" />' in contents)

    def testManagerCanDelegateManagerRoleForUsers(self):
        # a user with the Manager role can grant the Manager role
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )
        self.browser.open(self.usergroups_url)
        form = {
            '_authenticator': self._get_authenticator(),
            'users.id:records': self.normal_user,
            'users.roles:list:records': 'Manager',
            'form.button.Modify': 'Save',
            'form.submitted': 1,
        }
        post_data = urlencode(form)
        self.browser.post(self.usergroups_url, post_data)
        self.assertIn('Status: 200', str(self.browser.headers))

        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Manager', 'Authenticated'], roles)

    def testNonManagersCannotDelegateManagerRoleForUsers(self):
        # a user without the Manager role cannot delegate the Manager role
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')
        self.browser.open(self.usergroups_url)
        form = {
            '_authenticator': self._get_authenticator(),
            'users.id:records': self.normal_user,
            'users.roles:list:records': 'Manager',
            'form.button.Modify': 'Save',
            'form.submitted': 1,
        }
        post_data = urlencode(form)
        with self.assertRaises(zExceptions.Forbidden):
            self.browser.post(self.usergroups_url, post_data)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Member', 'Authenticated'], roles)

    def testNonManagersCanEditOtherRolesOfUsersWithManagerRole(self):
        roles = self.portal.acl_users.getUserById('root').getRoles()
        self.assertEqual(['Manager', 'Authenticated'], roles)
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')
        self.browser.open(self.usergroups_url)
        form = {
            '_authenticator': self._get_authenticator(),
            'users.id:records': 'root',
            'users.roles:list:records': ('Member', 'Manager'),
            'form.button.Modify': 'Save',
            'form.submitted': 1,
        }
        post_data = urlencode(form, doseq=True)
        self.browser.post(self.usergroups_url, post_data)
        roles = self.portal.acl_users.getUserById('root').getRoles()
        self.assertEqual(['Authenticated', 'Manager', 'Member'], sorted(roles))

    def testGroupManagerRoleCheckboxIsDisabledForNonManagers(self):
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')
        self.browser.open(self.groups_url)
        contents = self._simplify_white_space(self.browser.contents)
        self.assertTrue('<input type="checkbox" class="noborder" '
                        'name="group_Reviewers:list" value="Manager" '
                        'disabled="disabled" />' in contents)

    def testManagerCanDelegateManagerRoleForGroups(self):
        # a user with the Manager role can grant the Manager role
        roles = self.portal.acl_users.getGroupById('Reviewers').getRoles()
        self.assertEqual(['Reviewer', 'Authenticated'], roles)
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )
        self.browser.open(self.groups_url)
        form = {
            '_authenticator': self._get_authenticator(),
            'group_Reviewers:list': ('', 'Manager'),
            'form.button.Modify': 'Save',
            'form.submitted': 1,
        }
        post_data = urlencode(form, doseq=True)
        self.browser.post(self.groups_url, post_data)
        roles = self.portal.acl_users.getGroupById('Reviewers').getRoles()
        self.assertEqual(['Manager', 'Authenticated'], roles)

    def testNonManagersCannotDelegateManagerRoleForGroups(self):
        # a user without the Manager role cannot delegate the Manager role
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')

        self.browser.open(self.groups_url)
        form = {
            '_authenticator': self._get_authenticator(),
            'group_Reviewers:list': ('', 'Manager'),
            'form.button.Modify': 'Save',
            'form.submitted': 1,
        }
        post_data = urlencode(form, doseq=True)
        with self.assertRaises(zExceptions.Forbidden):
            self.browser.post(self.groups_url, post_data)
        # self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getGroupById('Reviewers').getRoles()
        self.assertEqual(['Reviewer', 'Authenticated'], roles)

    def testNonManagersCanEditOtherRolesOfGroupsWithManagerRole(self):
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')

        roles = self.portal.acl_users.getUserById('root').getRoles()
        self.assertEqual(['Manager', 'Authenticated'], roles)
        self.browser.open(self.groups_url)
        form = {
            '_authenticator': self._get_authenticator(),
            'group_Administrators:list': ('', 'Member', 'Manager'),
            'form.button.Modify': 'Save',
            'form.submitted': 1,
        }
        post_data = urlencode(form, doseq=True)
        self.browser.post(self.groups_url, post_data)
        # self.assertEqual(200, res.status)
        roles = self.portal.acl_users.getGroupById('Administrators').getRoles()
        self.assertEqual(['Authenticated', 'Manager', 'Member'], sorted(roles))

    def test_usergroup_usermembership_blocks_escalation(self):
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')

        # groups granting the Manager role shouldn't show as a valid option to
        # add
        self.browser.open(
            self.portal_url + '/@@usergroup-usermembership?userid=%s' % self.normal_user)
        contents = self._simplify_white_space(self.browser.contents)
        self.assertTrue(
            '<input type="checkbox" class="noborder" name="add:list" '
            'value="Administrators" disabled="disabled" />' in contents
        )

        # and should not be addable
        form = {
            '_authenticator': self._get_authenticator(),
            'add:list': 'Administrators',
            'form.submitted': 1,
        }
        post_data = urlencode(form)
        with self.assertRaises(zExceptions.Forbidden):
            self.browser.open(
                self.portal_url + '/@@usergroup-usermembership?userid=%s' % self.normal_user, post_data
            )
        # self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Member', 'Authenticated'], roles)

    def test_usergroup_groupmembership_blocks_escalation(self):
        # should not show section to add users for groups granting the Manager
        # role
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')

        self.browser.open(
            self.portal_url + '/@@usergroup-groupmembership?groupname=Administrators'
        )
        contents = self._simplify_white_space(self.browser.contents)
        self.assertFalse('Search for new group members' in contents)

        # and should not be addable if we try to force it
        form = {
            '_authenticator': self._get_authenticator(),
            'add:list': self.normal_user,
            'form.submitted': 1,
        }
        post_data = urlencode(form)
        with self.assertRaises(zExceptions.Forbidden):
            self.browser.post(
                self.portal_url + '/@@usergroup-groupmembership?groupname=Administrators', post_data
            )
        # self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Member', 'Authenticated'], roles)

    def test_user_registration_form_blocks_escalation(self):
        # groups granting the Manager role should not be available for
        # selection
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')
        self.browser.open(self.portal_url + '/@@new-user')
        contents = self._simplify_white_space(self.browser.contents)
        self.assertFalse(
            '<input class="label checkboxType" id="form.groups.0" '
            'name="form.groups" type="checkbox" value="Administrators '
            '(Administrators)" />' in contents
        )
        # and should not be getting that roles if we try to force it
        form = {
            '_authenticator': self._get_authenticator(),
            'form.widgets.username': 'newuser',
            'form.widgets.email': 'newuser@example.com',
            'form.widgets.password': 'secret',
            'form.widgets.password_ctl': 'secret',
            'form.widgets.groups:list': 'Administrators',
            'form.widgets.groups-empty-marker': '1',
            'form.buttons.register': 'Register',
        }
        post_data = urlencode(form)
        self.browser.post(self.portal_url + '/@@new-user', post_data)
        self.assertEqual(
            ['Member', 'Authenticated'],
            self.portal.acl_users.getUserById('newuser').getRoles())

    def test_users_overview_blocks_deleting_managers(self):
        # a user without the Manager role cannot delete a user with the
        # Manager role
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')

        self.browser.open(self.usergroups_url)
        contents = self._simplify_white_space(self.browser.contents)
        self.assertTrue(
            '<input type="checkbox" class="noborder notify" '
            'name="delete:list" value="root" title="Remove user " disabled="disabled" />'
            in contents)

        form = {
            '_authenticator': self._get_authenticator(),
            'users.id:records': 'root',
            'delete:list': 'root',
            'form.button.Modify': 'Save',
            'form.submitted': 1,
        }
        post_data = urlencode(form)
        with self.assertRaises(zExceptions.Forbidden):
            self.browser.post(self.usergroups_url, post_data)
        # self.assertEqual(403, res.status)
        user = self.portal.acl_users.getUserById('root')
        self.assertTrue(user is not None)

    def test_groups_overview_blocks_deleting_managers(self):
        # a user without the Manager role cannot delete a group with the
        # Manager role
        self.browser.addHeader(
            'Authorization', 'Basic siteadmin:secret')

        self.browser.open(self.groups_url)
        contents = self._simplify_white_space(self.browser.contents)
        self.assertTrue(
            '<input type="checkbox" class="noborder notify" '
            'name="delete:list" value="Administrators" disabled="disabled" />'
            in contents
        )

        form = {
            '_authenticator': self._get_authenticator(),
            'delete:list': 'Administrators',
            'form.button.Modify': 'Save',
            'form.submitted': 1,
        }
        post_data = urlencode(form)
        with self.assertRaises(zExceptions.Forbidden):
            self.browser.post(self.groups_url, post_data)
        # self.assertEqual(403, res.status)
        group = self.portal.acl_users.getGroupById('Administrators')
        self.assertTrue(group is not None)
