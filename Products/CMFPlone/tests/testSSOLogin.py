from plone.testing.z2 import Browser
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import TEST_USER_ROLES
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ILoginSchema
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from Products.CMFPlone.factory import addPloneSite
import transaction


class SSOLoginTestCase(PloneTestCase):

    def afterSetUp(self):
        PloneTestCase.afterSetUp(self)

        self.setRoles(['Manager'])
        addPloneSite(self.app, 'login_portal', content_profile_id='Products.ATContentTypes:default')
        addPloneSite(self.app, 'another_portal', content_profile_id='Products.ATContentTypes:default')

        self.browser = Browser(self.app)
        self.browser.handleErrors = False  # Don't get HTTP 500 pages

        self.login_portal = self.app.login_portal  # logins go here
        self.another_portal = self.app.another_portal  # another portal
        # The extra portals do not get a member setup from the base class.
        # Add our user to the other portals to simulate an ldap environment.
        for portal in (self.login_portal, self.another_portal):
            portal.acl_users.source_users.addUser(
                TEST_USER_ID,
                TEST_USER_NAME,
                TEST_USER_PASSWORD)
        for role in TEST_USER_ROLES:
            portal.acl_users.portal_role_manager.doAssignRoleToPrincipal(TEST_USER_ID, role)

        registry = self.login_portal.portal_registry

        # Configure the login portal to allow logins from our sites.
        registry['plone.allow_external_login_sites'] = (self.portal.absolute_url(),
                                                        self.another_portal.absolute_url())

        # Configure our sites to use the login portal for logins and logouts
        login_portal_url = self.login_portal.absolute_url()
        for portal in (self.portal, self.another_portal):
            reg = portal.portal_registry
            reg['plone.external_login_url'] = login_portal_url + '/login'
            reg['plone.external_logout_url'] = login_portal_url + '/logout'

        # Configure all sites to use a shared secret and set cookies per path
        # (normally they would have different domains.)
        for portal in (self.portal, self.login_portal, self.another_portal):
            session = portal.acl_users.session
            session._shared_secret = 'secret'
            session.path = portal.absolute_url_path()

        # Turn on self-registration
        self.portal.manage_permission('Add portal member',
                                      roles=['Manager', 'Anonymous'],
                                      acquire=0)

        transaction.commit()


class TestSSOLogin(SSOLoginTestCase):

    def test_loginAndLogout(self):
        browser = self.browser
        browser.open(self.portal.absolute_url())
        browser.getLink('Log in').click()
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'],
                         self.login_portal.absolute_url_path())
        # Without javascript we must click through
        browser.getForm('external_login_form').submit()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'],
                         self.portal.absolute_url_path())
        # Test logging in from another_portal
        browser.open(self.another_portal.absolute_url())
        browser.getLink('Log in').click()
        # No need to enter password this time
        browser.getForm('external_login_form').submit()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'],
                         self.another_portal.absolute_url_path())
        # Now logout
        browser.open(self.portal.absolute_url())
        browser.getLink('Log out').click()
        # Check we really logged out, there should be a login link
        browser.getLink('Log in')
        # Check we are logged out of the login_portal too
        browser.open(self.login_portal.absolute_url())
        browser.getLink('Log in')
        # Still need to logout of another_portal
        browser.open(self.another_portal.absolute_url())
        browser.getLink('Log out').click()
        browser.getLink('Log in')

    def test_requireLogin(self):
        browser = self.browser
        browser.handleErrors = True  # So unauthorized renders a login form
        # Login to the central portal
        browser.open(self.login_portal.absolute_url())
        browser.getLink('Log in').click()
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()
        # Check we are logged in centrally
        browser.getLink('Log out')
        # But not on the other portal
        browser.open(self.portal.absolute_url())
        browser.getLink('Log in')
        # Now open the protected doc
        protected_url = self.folder.absolute_url() + '/folder_contents'
        browser.open(protected_url)
        # Without javascript we must click through
        self.assertEqual(browser.getControl(name='came_from').value,
                         protected_url)
        browser.getForm('external_login_form').submit()
        self.assertEqual(browser.url, protected_url)
        browser.getLink('Log out')


class TestSSOLoginIframe(SSOLoginTestCase):

    def afterSetUp(self):
        SSOLoginTestCase.afterSetUp(self)
        # Configure our sites to use the iframe
        for portal in (self.portal, self.another_portal):
            portal.portal_registry['plone.external_login_iframe'] = True
        transaction.commit()

    def test_loginAndLogoutSSO(self):
        browser = self.browser
        browser.open(self.portal.absolute_url())
        browser.getLink('Log in').click()
        # The test browser does not support iframes
        form = browser.getForm(name='login_form')
        form.submit()
        # We are now inside the iframe
        self.assertTrue(
                browser.url.startswith(self.login_portal.absolute_url()))
        # The Link to get  a new password points back to self.portal
        link = browser.getLink('we can send you a new one')
        self.assertTrue(link.url.startswith(self.portal.absolute_url()))
        self.assertEqual(link.attrs['target'], '_parent')
        # So does the registration form
        link = browser.getLink('registration form')
        self.assertTrue(link.url.startswith(self.portal.absolute_url()))
        self.assertEqual(link.attrs['target'], '_parent')
        # Login
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'],
                         self.login_portal.absolute_url_path())
        # The external_login_form has a target attribute too (but difficult to
        # test for)
        self.assertTrue(browser.contents.find('target=') > 0)
        # Without javascript we must click through
        browser.getForm('external_login_form').submit()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'],
                         self.portal.absolute_url_path())
        # Now in another_portal
        browser.open(self.another_portal.absolute_url())
        browser.getLink('Log in').click()
        # The test browser does not support iframes
        form = browser.getForm(name='login_form')
        form.submit()
        # We are now inside the iframe
        self.assertTrue(
                browser.url.startswith(self.login_portal.absolute_url()))
        browser.getForm('external_login_form').submit()
        self.assertEqual(self.browser.cookies.getinfo('__ac')['path'],
                         self.another_portal.absolute_url_path())
        # Now logout
        browser.open(self.portal.absolute_url())
        browser.getLink('Log out').click()
        # Check we really logged out, there should be a login link
        browser.getLink('Log in')
        # The test browser does not support iframes
        form = browser.getForm(name='login_form')
        form.submit()
        # Check the registration form does not have an incorrect came_from link
        link = browser.getLink('registration form')
        self.assertFalse('came_from' in link.url)
        self.assertEqual(link.attrs['target'], '_parent')
        # Check we are logged out of the login_portal too
        browser.open(self.login_portal.absolute_url())
        browser.getLink('Log in')
        # Still need to logout of another_portal
        browser.open(self.another_portal.absolute_url())
        browser.getLink('Log out').click()
        browser.getLink('Log in')

    def test_requireLoginSSO(self):
        browser = self.browser
        browser.handleErrors = True  # So unauthorized renders a login form
        # Login to the central portal
        browser.open(self.login_portal.absolute_url())
        browser.getLink('Log in').click()
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()
        # Check we are logged in centrally
        browser.getLink('Log out')
        # But not on the other portal
        browser.open(self.portal.absolute_url())
        browser.getLink('Log in')
        # Now open the protected doc
        protected_url = self.folder.absolute_url() + '/folder_contents'
        browser.open(protected_url)
        # The test browser does not support iframes
        form = browser.getForm(name='login_form')
        self.assertEqual(browser.getControl(name='came_from').value,
                         protected_url)
        form.submit()
        # Without javascript we must click through
        self.assertEqual(browser.getControl(name='came_from').value,
                         protected_url)
        browser.getForm('external_login_form').submit()
        self.assertEqual(browser.url, protected_url)
        browser.getLink('Log out')
