from plone.app.users.tests.base import TestCase


class TestNewUser(TestCase):

    def test_new_user_as_site_administrator(self):
        self.portal.acl_users._doAddUser('siteadmin', 'secret', ['Site Administrator'], [])
        self.browser.addHeader('Authorization', 'Basic siteadmin:secret')
        self.browser.open('http://nohost/plone/new-user')
        self.browser.getControl('User Name').value = 'newuser'
        self.browser.getControl('E-mail').value = 'newuser@example.com'
        self.browser.getControl('Password').value = 'foobar'
        self.browser.getControl('Confirm password').value = 'foobar'
        self.browser.getControl('Site Administrators').selected = True
        self.browser.getControl('Register').click()

        # make sure the new user is in the Site Administrators group
        self.assertTrue('Site Administrator' in
            self.portal.acl_users.getUserById('newuser').getRoles())
