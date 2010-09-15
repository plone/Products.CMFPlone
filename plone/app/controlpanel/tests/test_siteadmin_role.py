import re
from cStringIO import StringIO
from urllib import urlencode
from plone.app.controlpanel.tests.cptc import UserGroupsControlPanelTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

setupPloneSite()


class TestSiteAdminRoleFunctional(UserGroupsControlPanelTestCase):

    def afterSetUp(self):
        super(TestSiteAdminRoleFunctional, self).afterSetUp()
        
        # add a user with the SiteAdmin role
        self.portal.portal_membership.addMember('siteadmin', 'secret', ['SiteAdmin'], [])
        
        token_re = re.compile(r'name="_authenticator" value="([^"]+)"')
        res = self.publish('/plone/@@usergroup-userprefs', basic='root:secret')
        self.manager_token = token_re.search(res.getOutput()).group(1)
        res = self.publish('/plone/@@usergroup-userprefs', basic='siteadmin:secret')
        self.siteadmin_token = token_re.search(res.getOutput()).group(1)
        
        self.normal_user = 'DIispfuF'

    def testControlPanelOverview(self):
        # make sure we can view the Site Setup page,
        # at both old and new URLs
        res = self.publish('/plone/plone_control_panel', 'siteadmin:secret')
        self.assertEqual(200, res.status)
        res = self.publish('/plone/@@overview-controlpanel', 'siteadmin:secret')
        self.assertEqual(200, res.status)

    def testUserManagerRoleCheckboxIsDisabledForNonManagers(self):
        res = self.publish('/plone/@@usergroup-userprefs', basic='siteadmin:secret')
        self.assertTrue('<input type="checkbox" class="noborder" '
                        'name="users.roles:list:records" value="Manager" '
                        'disabled="disabled" />' in res.getOutput())

    def testManagerCanDelegateManagerRoleForUsers(self):
        # a user with the Manager role can grant the Manager role
        form = {
            '_authenticator': self.manager_token,
            'users.id:records': self.normal_user,
            'users.roles:list:records': 'Manager',
            'form.button.Modify': 'Apply Changes',
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
            'form.button.Modify': 'Apply Changes',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish('/plone/@@usergroup-userprefs',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Member', 'Authenticated'], roles)

    def testGroupManagerRoleCheckboxIsDisabledForNonManagers(self):
        res = self.publish('/plone/@@usergroup-groupprefs', basic='siteadmin:secret')
        self.assertTrue('<input type="checkbox" class="noborder" '
                        'name="group_Reviewers:list" value="Manager" '
                        'disabled="disabled" />' in res.getOutput())

    def testManagerCanDelegateManagerRoleForGroups(self):
        # a user with the Manager role can grant the Manager role
        form = {
            '_authenticator': self.manager_token,
            'group_Reviewers:list': '',
            'group_Reviewers:list': 'Manager',
            'form.button.Modify': 'Apply Changes',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
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
            'group_Reviewers:list': '',
            'group_Reviewers:list': 'Manager',
            'form.button.Modify': 'Apply Changes',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish('/plone/@@usergroup-groupprefs',
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getGroupById('Reviewers').getRoles()
        self.assertEqual(['Reviewer', 'Authenticated'], roles)

    def test_usergroup_usermembership_blocks_escalation(self):
        # groups granting the Manager role shouldn't show as a valid option to add
        res = self.publish('/plone/@@usergroup-usermembership?userid=%s' % self.normal_user,
                           basic='siteadmin:secret')
        self.assertTrue('<input type="checkbox" class="noborder" name="add:list" '
                        'value="Administrators" disabled="disabled" />' in res.getOutput())
        
        # and should not be addable
        form = {
            '_authenticator': self.siteadmin_token,
            'add:list': 'Administrators',
            'form.submitted': 1,
            }
        post_data = StringIO(urlencode(form))
        res = self.publish('/plone/@@usergroup-usermembership?userid=%s' % self.normal_user,
                           request_method='POST', stdin=post_data,
                           basic='siteadmin:secret')
        self.assertEqual(403, res.status)
        roles = self.portal.acl_users.getUserById(self.normal_user).getRoles()
        self.assertEqual(['Member', 'Authenticated'], roles)


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
