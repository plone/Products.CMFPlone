from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel import tests
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from Products.CMFPlone.utils import get_installer
from Products.GenericSetup.tool import UNKNOWN
from zope.component import getMultiAdapter
from zope.configuration import xmlconfig

import unittest


class AddonsIntegrationTest(unittest.TestCase):
    """Test that the addons control panel is working nicely."""

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.installer = get_installer(self.portal, self.request)

    def test_addons_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="prefs_install_products_form"
        )
        self.assertTrue(view())

    def test_addons_in_controlpanel(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")
        self.assertIn(
            "QuickInstaller",
            [a.getAction(self)["id"] for a in self.controlpanel.listActions()],
        )

    def test_installer_view(self):
        from Products.CMFPlone.controlpanel.browser.quickinstaller import InstallerView

        view = getMultiAdapter((self.portal, self.portal.REQUEST), name="installer")
        self.assertTrue(isinstance(view, InstallerView))
        self.assertTrue(isinstance(self.installer, InstallerView))

    def _test_install_uninstall(self, product):
        self.assertTrue(self.installer.is_product_installable(product))
        self.assertFalse(self.installer.is_product_installed(product))
        # Install the product.
        self.assertTrue(self.installer.install_product(product))
        # Even after install this is still installable,
        # because that simply means it has an install profile.
        self.assertTrue(self.installer.is_product_installable(product))
        self.assertTrue(self.installer.is_product_installed(product))
        # Uninstall the product.
        self.assertTrue(self.installer.uninstall_product(product))
        self.assertTrue(self.installer.is_product_installable(product))
        self.assertFalse(self.installer.is_product_installed(product))

    def test_install_uninstall_cmfplacefulworkflow_without_products(self):
        try:
            import Products.CMFPlacefulWorkflow

            Products.CMFPlacefulWorkflow  # pyflakes
        except ImportError:
            return
        self._test_install_uninstall("CMFPlacefulWorkflow")

    def test_install_uninstall_cmfplacefulworkflow_with_products(self):
        try:
            import Products.CMFPlacefulWorkflow

            Products.CMFPlacefulWorkflow  # pyflakes
        except ImportError:
            return
        self._test_install_uninstall("Products.CMFPlacefulWorkflow")

    def test_install_uninstall_package(self):
        try:
            import plone.session

            plone.session  # pyflakes
        except ImportError:
            return
        self._test_install_uninstall("plone.session")

    def test_unknown_package(self):
        product = "no.product"
        self.assertFalse(self.installer.is_product_installable(product))
        self.assertFalse(self.installer.is_product_installed(product))
        # Install the product.
        self.assertFalse(self.installer.install_product(product))
        self.assertFalse(self.installer.is_product_installable(product))
        self.assertFalse(self.installer.is_product_installed(product))
        # Uninstall the product.
        self.assertFalse(self.installer.uninstall_product(product))
        self.assertFalse(self.installer.is_product_installable(product))
        self.assertFalse(self.installer.is_product_installed(product))

    def test_plone_app_upgrade_not_installable(self):
        installable = self.installer.is_product_installable
        # Test a few current and future plone.app.upgrade versions.
        self.assertFalse(installable("plone.app.upgrade"))
        self.assertFalse(installable("plone.app.upgrade.v30"))
        self.assertFalse(installable("plone.app.upgrade.v40"))
        self.assertFalse(installable("plone.app.upgrade.v50"))
        self.assertFalse(installable("plone.app.upgrade.v51"))
        self.assertFalse(installable("plone.app.upgrade.v52"))
        self.assertFalse(installable("plone.app.upgrade.v53"))
        self.assertFalse(installable("plone.app.upgrade.v60"))
        self.assertFalse(installable("plone.app.upgrade.v61"))
        self.assertFalse(installable("plone.app.upgrade.v62"))
        self.assertFalse(installable("plone.app.upgrade.v63"))
        self.assertFalse(installable("plone.app.upgrade.v70"))

    def test_latest_upgrade_profiles3(self):
        xmlconfig.file(
            "test_upgrades1.zcml",
            package=tests,
            context=self.layer["configurationContext"],
        )
        latest = self.installer.get_latest_upgrade_step(
            "Products.CMFPlone:testfixture1"
        )
        self.assertEqual(latest, "3")

    def test_latest_upgrade_profiles2(self):
        # make sure strings don't break things
        # note that pkg_resources interprets 1 as
        # ''00000001', which is > 'banana'
        xmlconfig.file(
            "test_upgrades2.zcml",
            package=tests,
            context=self.layer["configurationContext"],
        )
        latest = self.installer.get_latest_upgrade_step(
            "Products.CMFPlone:testfixture2"
        )
        self.assertEqual(latest, "3")

    def test_latest_upgrade_profiles_unknown(self):
        latest = self.installer.get_latest_upgrade_step("no.profile")
        self.assertEqual(latest, UNKNOWN)

    def test_is_profile_installed(self):
        self.assertFalse(self.installer.is_profile_installed("foo:default"))
        self.assertTrue(
            self.installer.is_profile_installed("plone.app.dexterity:default")
        )
        self.assertTrue(
            self.installer.is_profile_installed("profile-plone.app.dexterity:default")
        )

    def test_is_product_installed(self):
        self.assertFalse(self.installer.is_product_installed("foo"))
        self.assertFalse(self.installer.is_product_installed("plone.session"))
        self.assertTrue(self.installer.is_product_installed("plone.app.dexterity"))

    def test_get_install_profiles(self):
        # Note: this method name is a bit of a misnomer.
        # It lists *all* extension profiles.
        # The method seems unneeded.
        self.assertEqual(self.installer.get_install_profiles("foo"), [])
        session_profiles = self.installer.get_install_profiles("plone.session")
        self.assertIn("plone.session:default", session_profiles)
        self.assertIn("plone.session:uninstall", session_profiles)
        self.assertEqual(
            self.installer.get_install_profiles("plone.app.dexterity"),
            ["plone.app.dexterity:default", "plone.app.dexterity:testing"],
        )
        try:
            import Products.CMFPlacefulWorkflow

            Products.CMFPlacefulWorkflow  # pyflakes
        except ImportError:
            return
        self.assertEqual(
            self.installer.get_install_profiles("CMFPlacefulWorkflow"),
            [
                "Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow",
                "Products.CMFPlacefulWorkflow:base",
                "Products.CMFPlacefulWorkflow:uninstall",
            ],
        )
        self.assertEqual(
            self.installer.get_install_profiles("Products.CMFPlacefulWorkflow"),
            [
                "Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow",
                "Products.CMFPlacefulWorkflow:base",
                "Products.CMFPlacefulWorkflow:uninstall",
            ],
        )

    def test_get_install_profile(self):
        self.assertIsNone(self.installer.get_install_profile("foo"))
        profile = self.installer.get_install_profile("plone.session")
        self.assertEqual(profile["id"], "plone.session:default")
        profile = self.installer.get_install_profile("plone.app.dexterity")
        self.assertEqual(profile["id"], "plone.app.dexterity:default")
        try:
            import Products.CMFPlacefulWorkflow

            Products.CMFPlacefulWorkflow  # pyflakes
        except ImportError:
            return
        profile = self.installer.get_install_profile("CMFPlacefulWorkflow")
        self.assertEqual(
            profile["id"], "Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow"
        )
        profile = self.installer.get_install_profile("Products.CMFPlacefulWorkflow")
        self.assertEqual(
            profile["id"], "Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow"
        )

    def test_get_uninstall_profile(self):
        self.assertIsNone(self.installer.get_uninstall_profile("foo"))
        profile = self.installer.get_uninstall_profile("plone.session")
        self.assertEqual(profile["id"], "plone.session:uninstall")
        profile = self.installer.get_uninstall_profile("plone.app.dexterity")
        self.assertIsNone(profile)
        try:
            import Products.CMFPlacefulWorkflow

            Products.CMFPlacefulWorkflow  # pyflakes
        except ImportError:
            return
        profile = self.installer.get_uninstall_profile("CMFPlacefulWorkflow")
        self.assertEqual(profile["id"], "Products.CMFPlacefulWorkflow:uninstall")
        profile = self.installer.get_uninstall_profile("Products.CMFPlacefulWorkflow")
        self.assertEqual(profile["id"], "Products.CMFPlacefulWorkflow:uninstall")

    def test_get_product_version(self):
        self.assertFalse(self.installer.get_product_version("foo"))
        version = self.installer.get_product_version("plone.session")
        self.assertIn(".", version)
        version = self.installer.get_product_version("plone.app.dexterity")
        self.assertIn(".", version)
        try:
            import Products.CMFPlacefulWorkflow

            Products.CMFPlacefulWorkflow  # pyflakes
        except ImportError:
            return
        version = self.installer.get_product_version("CMFPlacefulWorkflow")
        self.assertIn(".", version)
        version = self.installer.get_product_version("Products.CMFPlacefulWorkflow")
        self.assertIn(".", version)

    def test_upgrade_info(self):
        # an unknown product
        self.assertEqual(self.installer.upgrade_info("foo"), {})
        # a not yet/ uninstalled product
        info = self.installer.upgrade_info("plone.session")
        self.assertEqual(self.installer.upgrade_info("plone.session"), {})
        # an installed product
        info = self.installer.upgrade_info("plone.app.dexterity")
        self.assertFalse(info["available"])
        self.assertFalse(info["required"])
        self.assertNotEqual(info["installedVersion"], UNKNOWN)
        self.assertEqual(info["installedVersion"], info["newVersion"])
        # fake an earlier version
        ps = self.portal.portal_setup
        ps.setLastVersionForProfile("plone.app.dexterity:default", "2002")
        info = self.installer.upgrade_info("plone.app.dexterity")
        self.assertTrue(info["available"])
        self.assertTrue(info["required"])
        self.assertEqual(info["installedVersion"], "2002")
        # upgrade the product
        self.assertTrue(self.installer.upgrade_product("plone.app.dexterity"))
        info = self.installer.upgrade_info("plone.app.dexterity")
        self.assertFalse(info["available"])
        self.assertFalse(info["required"])
        self.assertNotEqual(info["installedVersion"], UNKNOWN)
        self.assertEqual(info["installedVersion"], info["newVersion"])

    def test_upgrade_product(self):
        # an unknown product
        self.assertFalse(self.installer.upgrade_product("foo"))

        # We do not complain about a not-yet/ uninstalled product.
        self.assertTrue(self.installer.upgrade_product("plone.session"))
        info = self.installer.upgrade_info("plone.session")
        self.assertEqual(info, {})

        # We do not complain about an up to date product.
        self.assertTrue(self.installer.upgrade_product("plone.app.dexterity"))
        info = self.installer.upgrade_info("plone.app.dexterity")
        self.assertNotEqual(info["installedVersion"], UNKNOWN)
        self.assertEqual(info["installedVersion"], info["newVersion"])
        # fake an earlier version
        ps = self.portal.portal_setup
        ps.setLastVersionForProfile("plone.app.dexterity:default", "2002")
        info = self.installer.upgrade_info("plone.app.dexterity")
        self.assertEqual(info["installedVersion"], "2002")
        # upgrade the product
        self.assertTrue(self.installer.upgrade_product("plone.app.dexterity"))
        info = self.installer.upgrade_info("plone.app.dexterity")
        self.assertEqual(info["installedVersion"], info["newVersion"])

        # Try a Product too (not yet installed).
        info = self.installer.upgrade_info("Products.CMFPlacefulWorkflow")
        self.assertEqual(info, {})
        self.assertTrue(self.installer.upgrade_product("Products.CMFPlacefulWorkflow"))
        info = self.installer.upgrade_info("Products.CMFPlacefulWorkflow")
        self.assertEqual(info, {})
        info = self.installer.upgrade_info("CMFPlacefulWorkflow")
        self.assertEqual(info, {})
        self.assertTrue(self.installer.upgrade_product("CMFPlacefulWorkflow"))
        info = self.installer.upgrade_info("CMFPlacefulWorkflow")
        self.assertEqual(info, {})
        # fake a version
        ps = self.portal.portal_setup
        ps.setLastVersionForProfile(
            "Products.CMFPlacefulWorkflow:CMFPlacefulWorkflow", "0.0"
        )
        info = self.installer.upgrade_info("Products.CMFPlacefulWorkflow")
        self.assertEqual(info["installedVersion"], "0.0")
        info = self.installer.upgrade_info("CMFPlacefulWorkflow")
        self.assertEqual(info["installedVersion"], "0.0")
        # upgrade the product
        self.assertTrue(self.installer.upgrade_product("CMFPlacefulWorkflow"))
        info = self.installer.upgrade_info("CMFPlacefulWorkflow")
        self.assertEqual(info["installedVersion"], info["newVersion"])
        info = self.installer.upgrade_info("Products.CMFPlacefulWorkflow")
        self.assertEqual(info["installedVersion"], info["newVersion"])

    def test_install_product(self):
        # an unknown product
        self.assertFalse(self.installer.install_product("foo"))

        # an uninstalled product
        self.assertFalse(self.installer.is_product_installed("plone.session"))
        self.assertTrue(self.installer.install_product("plone.session"))
        self.assertTrue(self.installer.is_product_installed("plone.session"))

        # We complain a bit when installing an already installed product.
        self.assertTrue(self.installer.is_product_installed("plone.app.dexterity"))
        self.assertFalse(self.installer.install_product("plone.app.dexterity"))
        self.assertTrue(self.installer.is_product_installed("plone.app.dexterity"))

        # Try a Product too.
        self.assertFalse(self.installer.is_product_installed("CMFPlacefulWorkflow"))
        self.assertTrue(self.installer.install_product("CMFPlacefulWorkflow"))
        self.assertTrue(self.installer.is_product_installed("CMFPlacefulWorkflow"))
        self.assertTrue(
            self.installer.is_product_installed("Products.CMFPlacefulWorkflow")
        )
        # undo
        self.assertTrue(self.installer.uninstall_product("CMFPlacefulWorkflow"))
        self.assertFalse(
            self.installer.is_product_installed("Products.CMFPlacefulWorkflow")
        )
        # redo with 'Products.'
        self.assertTrue(self.installer.install_product("Products.CMFPlacefulWorkflow"))
        self.assertTrue(self.installer.is_product_installed("CMFPlacefulWorkflow"))
        self.assertTrue(
            self.installer.is_product_installed("Products.CMFPlacefulWorkflow")
        )

    def test_uninstall_product(self):
        # an unknown product
        self.assertFalse(self.installer.uninstall_product("foo"))

        # We do not complain about an already uninstalled product.
        self.assertFalse(self.installer.is_product_installed("plone.session"))
        self.assertTrue(self.installer.uninstall_product("plone.session"))
        self.assertFalse(self.installer.is_product_installed("plone.session"))

        # We do complain about an installed product without uninstall profile.
        # Dexterity cannot be uninstalled.
        self.assertTrue(self.installer.is_product_installed("plone.app.dexterity"))
        self.assertFalse(self.installer.uninstall_product("plone.app.dexterity"))
        self.assertTrue(self.installer.is_product_installed("plone.app.dexterity"))

        # Try a Product too.
        self.assertTrue(self.installer.install_product("CMFPlacefulWorkflow"))
        self.assertTrue(self.installer.uninstall_product("CMFPlacefulWorkflow"))
        self.assertFalse(self.installer.is_product_installed("CMFPlacefulWorkflow"))
        self.assertFalse(
            self.installer.is_product_installed("Products.CMFPlacefulWorkflow")
        )
        # Again with 'Products.'
        self.assertTrue(self.installer.install_product("Products.CMFPlacefulWorkflow"))
        self.assertTrue(
            self.installer.uninstall_product("Products.CMFPlacefulWorkflow")
        )
        self.assertFalse(self.installer.is_product_installed("CMFPlacefulWorkflow"))
        self.assertFalse(
            self.installer.is_product_installed("Products.CMFPlacefulWorkflow")
        )


def dummy_handler():
    pass
