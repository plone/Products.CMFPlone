from Products.Five.testbrowser import Browser
from Products.PloneTestCase import ptc

ptc.setupPloneSite(id=ptc.portal_name)
ptc.setupPloneSite(id='login_portal')

class TestSSOLogin(ptc.FunctionalTestCase):

    def afterSetUp(self):
        ptc.FunctionalTestCase.afterSetUp(self)

        self.browser = Browser()
        self.browser.handleErrors = False # Don't get HTTP 500 pages

        self.login_portal = self.app.login_portal # logins go here
        # The login portal does not get extra setup from the base class.
        # Add our user to the login_portal to simulate an ldap equivalent.
        self.login_portal.acl_users.userFolderAddUser(
            ptc.default_user, ptc.default_password, ['Member'], []
            )

        # Configure the login portal to allow logins from our site.
        self.login_portal.portal_properties.site_properties._updateProperty(
            'allow_external_login_sites', [self.portal.absolute_url()]
            )

        # Configure our site to use the login portal for logins and logouts
        site_properties = self.portal.portal_properties.site_properties
        login_portal_url = self.login_portal.absolute_url()
        site_properties._updateProperty('external_login_url', login_portal_url + '/login')
        site_properties._updateProperty('external_logout_url', login_portal_url + '/logout')

        # Configure both sites to use a shared secret and set cookies per path
        # (normally they would have different domains.)
        for portal in (self.portal, self.login_portal):
            session = portal.acl_users.session
            session._shared_secret = 'secret'
            session.path = portal.absolute_url_path()

    def test_loginAndLogout(self):
        browser = self.browser
        browser.open(self.portal.absolute_url())
        browser.getLink('Log in').click()
        browser.getControl(name='__ac_name').value = ptc.default_user
        browser.getControl(name='__ac_password').value = ptc.default_password
        browser.getControl(name='submit').click()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'], self.login_portal.absolute_url_path())
        # Without javascript we must click through
        browser.getForm('external_login_form').submit()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'], self.portal.absolute_url_path())
        # Now logout
        browser.open(self.portal.absolute_url())
        browser.getLink('Log out').click()
        # Check we really logged out, there should be a login link
        browser.getLink('Log in')
        # Check we are logged out of the login_portal too
        browser.open(self.login_portal.absolute_url())
        browser.getLink('Log in')


class TestSSOLoginIframe(TestSSOLogin):

    def afterSetUp(self):
        TestSSOLogin.afterSetUp(self)
        # Configure our site to use the iframe
        site_properties = self.portal.portal_properties.site_properties
        site_properties._updateProperty('external_login_iframe', True)

    def test_loginAndLogout(self):
        browser = self.browser
        browser.open(self.portal.absolute_url())
        browser.getLink('Log in').click()
        # The test browser does not support iframes
        form = browser.getForm(name='login_form')
        form.submit()
        # We are now inside the iframe
        browser.url.startswith(self.login_portal.absolute_url())
        # The Link to get  a new password points back to self.portal
        link = browser.getLink('we can send you a new one')
        self.failUnless(link.url.startswith(self.portal.absolute_url()))
        self.assertEqual(link.attrs['target'], '_parent')
        # Login
        browser.getControl(name='__ac_name').value = ptc.default_user
        browser.getControl(name='__ac_password').value = ptc.default_password
        browser.getControl(name='submit').click()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'], self.login_portal.absolute_url_path())
        # The external_login_form has a target attribute too (but difficult to test for)
        self.failUnless(browser.contents.find('target=') > 0)
        # Without javascript we must click through
        browser.getForm('external_login_form').submit()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'], self.portal.absolute_url_path())
        # Now logout
        browser.open(self.portal.absolute_url())
        browser.getLink('Log out').click()
        # Check we really logged out, there should be a login link
        browser.getLink('Log in')
        # Check we are logged out of the login_portal too
        browser.open(self.login_portal.absolute_url())
        browser.getLink('Log in')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSSOLogin))
    suite.addTest(makeSuite(TestSSOLoginIframe))
    return suite
