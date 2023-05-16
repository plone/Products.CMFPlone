from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.zope import Browser
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter

import unittest


class AddonsControlPanelFunctionalTest(unittest.TestCase):
    """Test that the add-ons control panel works nicely."""

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            "Authorization", f"Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        )

    def test_addons_controlpanel_link(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink("Add-ons").click()

    def test_addons_controlpanel_backlink(self):
        self.browser.open("%s/prefs_install_products_form" % self.portal_url)
        self.assertTrue("General" in self.browser.contents)

    def test_addons_controlpanel_sidebar(self):
        self.browser.open("%s/prefs_install_products_form" % self.portal_url)
        self.browser.getLink("Site Setup").click()
        self.assertTrue(self.browser.url.endswith("/plone/@@overview-controlpanel"))

    def test_addons_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="prefs_install_products_form"
        )
        self.assertTrue(view())

    def test_addons_controlpanel_no_upgrades(self):
        self.browser.open("%s/prefs_install_products_form" % self.portal_url)
        self.assertIn("No upgrades in this corner", self.browser.contents)

    def test_addons_controlpanel_installable(self):
        self.browser.open("%s/prefs_install_products_form" % self.portal_url)
        # We expect a few standard add-ons.
        self.assertIn("Workflow Policy Support", self.browser.contents)
        self.assertIn("Multilingual Support", self.browser.contents)
        self.assertIn("plone.session", self.browser.contents)

    def test_addons_controlpanel_not_installable(self):
        self.browser.open("%s/prefs_install_products_form" % self.portal_url)
        # We do not expect some other add-ons.
        self.assertNotIn("plone.app.upgrade", self.browser.contents)
        self.assertNotIn("Products.CMFPlone", self.browser.contents)

    def test_addons_controlpanel_install_and_uninstall_all(self):
        self.browser.open("%s/prefs_install_products_form" % self.portal_url)
        self.assertNotIn("Installed", self.browser.contents)
        self.assertNotIn("Uninstalled", self.browser.contents)

        # In a fresh site there should be no uninstall buttons.
        # If there is one, it is likely an upgrade profile that should be hidden.
        # This could change: we might for example install a theme by default
        # but make it uninstallable.  The logic in this test should be updated then.
        try:
            button = self.browser.getControl("Uninstall", index=0)
        except LookupError:
            # This is good.
            pass
        else:
            # We cannot easily see what the Uninstall button is for.
            # We have to get the form with a private attribute.
            raise AssertionError(
                f"Uninstall button found. Probably an upgrade profile needs to be hidden. {button._form.text}"
            )

        # It is hard to determine which exact product will be installed
        # by clicking on a button, because they are all called 'Install'.
        # We install all available products.
        for buttons in range(12):
            try:
                self.browser.getControl("Install", index=buttons)
            except LookupError:
                break
        else:
            # Either our test logic is off, or the code that determines
            # which products are installable is actually wrong.
            raise AssertionError("Too many Install buttons.")
        # Click all install buttons.
        for button in range(buttons):
            # Always install the first.
            self.browser.getControl("Install", index=0).click()
            self.assertIn("Installed", self.browser.contents)
        # There are no more install buttons.
        with self.assertRaises(LookupError):
            self.browser.getControl("Install", index=0)
        # There should now be just as many Uninstall buttons.
        self.browser.getControl("Uninstall", index=buttons - 1)
        for button in range(buttons):
            # Always uninstall the first.
            self.browser.getControl("Uninstall", index=0).click()
            self.assertIn("Uninstalled", self.browser.contents)
        # There are no more uninstall buttons.
        with self.assertRaises(LookupError):
            self.browser.getControl("Uninstall", index=0)
        # Instead, we could install all again if we want.
        self.browser.getControl("Install", index=buttons - 1)
