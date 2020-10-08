from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.testing import \
    PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from zope.component import getUtility

import unittest


class SecurityControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the security control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ISecuritySchema, prefix="plone")
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )

    def test_security_control_panel_link(self):
        self.browser.open(
            "%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('Security').click()

    def test_security_control_panel_backlink(self):
        self.browser.open(
            "%s/@@security-controlpanel" % self.portal_url)
        self.assertTrue("Security" in self.browser.contents)

    def test_security_control_panel_sidebar(self):
        self.browser.open(
            "%s/@@security-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertTrue(
            self.browser.url.endswith('/plone/@@overview-controlpanel')
        )

    def test_enable_self_reg(self):
        self.browser.open(
            "%s/@@security-controlpanel" % self.portal_url)
        self.browser.getControl('Enable self-registration').selected = True
        self.browser.getControl('Save').click()

        self.assertEqual(self.settings.enable_self_reg, True)

    def test_enable_user_pwd_choice(self):
        self.browser.open(
            "%s/@@security-controlpanel" % self.portal_url)
        self.browser.getControl(
            'Let users select their own passwords').selected = True
        self.browser.getControl('Save').click()

        self.assertEqual(self.settings.enable_user_pwd_choice, True)

    def test_enable_user_folders(self):
        self.browser.open(
            "%s/@@security-controlpanel" % self.portal_url)
        self.browser.getControl(
            'Enable User Folders').selected = True
        self.browser.getControl('Save').click()

        self.assertEqual(self.settings.enable_user_folders, True)

    def test_allow_anon_views_about(self):
        self.browser.open(
            "%s/@@security-controlpanel" % self.portal_url)
        self.browser.getControl(
            "Allow anyone to view 'about' information").selected = True
        self.browser.getControl('Save').click()

        self.assertEqual(self.settings.allow_anon_views_about, True)

    def test_use_email_as_login(self):
        self.browser.open(
            "%s/@@security-controlpanel" % self.portal_url)
        self.browser.getControl(
            "Use email address as login name").selected = True
        self.browser.getControl('Save').click()

        self.assertEqual(self.settings.use_email_as_login, True)

    def test_use_uuid_as_userid(self):
        self.browser.open(
            "%s/@@security-controlpanel" % self.portal_url)
        self.browser.getControl(
            "Use UUID user ids").selected = True
        self.browser.getControl('Save').click()

        self.assertEqual(self.settings.use_uuid_as_userid, True)
