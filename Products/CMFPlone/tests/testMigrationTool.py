from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.tests import PloneTestCase


# Python 3 is only supported on 5.2+.
# This means you can not upgrade from 5.1 or earlier.
START_PROFILE = "5200"


class TestMigrationTool(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.migration = getToolByName(self.portal, "portal_migration")
        self.setup = getToolByName(self.portal, "portal_setup")

    def testMigrationFinished(self):
        self.assertEqual(
            self.migration.getInstanceVersion(),
            self.migration.getFileSystemVersion(),
            "Migration failed",
        )

    def testMigrationNeedsUpgrading(self):
        self.assertFalse(self.migration.needUpgrading(), "Migration needs upgrading")

    def testMigrationNeedsUpdateRole(self):
        self.assertFalse(self.migration.needUpdateRole(), "Migration needs role update")

    def testMigrationNeedsRecatalog(self):
        self.assertFalse(self.migration.needRecatalog(), "Migration needs recataloging")

    def testListSetupUpgradeSteps(self):
        # There should be no upgrade steps from the current version
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertEqual(len(upgrades), 0)

    def testListOwnUpgradeSteps(self):
        # There should be no upgrade steps from the current version
        upgrades = self.migration.listUpgrades()
        self.assertEqual(len(upgrades), 0)

    def testDoUpgrades(self):
        self.setRoles(["Manager"])
        self.setup.setLastVersionForProfile(_DEFAULT_PROFILE, START_PROFILE)
        upgrades = self.migration.listUpgrades()
        self.assertGreater(len(upgrades), 0)

        request = self.portal.REQUEST
        request.form["profile_id"] = _DEFAULT_PROFILE

        steps = []
        for upgrade in upgrades:
            if isinstance(upgrade, list):
                steps.extend([s["id"] for s in upgrade])
            else:
                steps.append(upgrade["id"])

        request.form["upgrades"] = steps
        self.setup.manage_doUpgrades(request=request)

        # And we have reached our current profile version
        current = self.setup.getVersionForProfile(_DEFAULT_PROFILE)
        current = tuple(current.split("."))
        last = self.setup.getLastVersionForProfile(_DEFAULT_PROFILE)
        self.assertEqual(last, current)

        # There are no more upgrade steps available
        upgrades = self.migration.listUpgrades()
        self.assertEqual(len(upgrades), 0)

    def testUpgrade(self):
        self.setRoles(["Manager"])
        self.setup.setLastVersionForProfile(_DEFAULT_PROFILE, START_PROFILE)
        self.migration.upgrade()

        # And we have reached our current profile version
        current = self.setup.getVersionForProfile(_DEFAULT_PROFILE)
        current = tuple(current.split("."))
        last = self.setup.getLastVersionForProfile(_DEFAULT_PROFILE)
        self.assertEqual(last, current)

        # There are no more upgrade steps available
        upgrades = self.migration.listUpgrades()
        self.assertEqual(len(upgrades), 0)


class TestMigrationWithExtraUpgrades(PloneTestCase.PloneTestCase):
    """Test a migration with a too new upgrade available.

    There should be no upgrade steps newer than the current version.
    If our FS profile version is 5, and there is an upgrade to 6,
    we do not want to see it.  This just means we have a newer
    plone.app.upgrade, which is fine.
    """

    def afterSetUp(self):
        from Products.GenericSetup.upgrade import _registerUpgradeStep
        from Products.GenericSetup.upgrade import UpgradeStep

        self.migration = getToolByName(self.portal, "portal_migration")
        self.setup = getToolByName(self.portal, "portal_setup")

        def failing_upgrade(context):
            raise AssertionError("Too new upgrade should not be run!")

        # Register a too new upgrade.
        fs_version = self.migration.getFileSystemVersion()
        new_version = str(int(fs_version) + 1)
        new_step = UpgradeStep(
            "Too new upgrade",
            _DEFAULT_PROFILE,
            fs_version,
            new_version,
            "",
            failing_upgrade,
            None,
            "1",
        )
        self.step_id = new_step.id
        _registerUpgradeStep(new_step)

    def beforeTearDown(self):
        # Remove the extra step from the upgrade registry,
        # otherwise this bleeds over into other tests.
        from Products.GenericSetup.upgrade import _upgrade_registry

        profile_steps = _upgrade_registry.getUpgradeStepsForProfile(_DEFAULT_PROFILE)
        profile_steps.pop(self.step_id, None)

    def testListUpgradeStepsNotTooNew(self):
        # portal_setup happily reports the newer upgrade
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertGreater(len(upgrades), 0)
        # Our migration tool no longer shows it.
        upgrades = self.migration.listUpgrades()
        self.assertEqual(len(upgrades), 0)

    def testUpgrade(self):
        self.setRoles(["Manager"])
        self.setup.setLastVersionForProfile(_DEFAULT_PROFILE, START_PROFILE)
        self.migration.upgrade()

        # And we have reached our current profile version
        current = self.setup.getVersionForProfile(_DEFAULT_PROFILE)
        current = tuple(current.split("."))
        last = self.setup.getLastVersionForProfile(_DEFAULT_PROFILE)
        self.assertEqual(last, current)

        # There are no more upgrade steps available
        upgrades = self.migration.listUpgrades()
        self.assertEqual(len(upgrades), 0)


class TestAddonList(PloneTestCase.PloneTestCase):
    def test_addon_safe(self):
        from Products.CMFPlone.MigrationTool import Addon

        addon = Addon(profile_id=_DEFAULT_PROFILE)
        self.assertTrue(addon.safe())
        addon = Addon(profile_id=_DEFAULT_PROFILE, check_module="Products.CMFPlone")
        self.assertTrue(addon.safe())
        addon = Addon(
            profile_id=_DEFAULT_PROFILE, check_module="Products.CMFPlone.foobarbaz"
        )
        self.assertFalse(addon.safe())

    def test_addon_repr(self):
        from Products.CMFPlone.MigrationTool import Addon

        addon = Addon(profile_id="foo")
        self.assertEqual(repr(addon), "<Addon profile foo>")
        self.assertEqual(str(addon), "<Addon profile foo>")

    def test_upgrade_all(self):
        from Products.CMFPlone.MigrationTool import Addon
        from Products.CMFPlone.MigrationTool import AddonList

        # real ones:
        cmfeditions = Addon(profile_id="Products.CMFEditions:CMFEditions")
        discussion = Addon(profile_id="plone.app.discussion:default")
        # real one with failing check_module:
        dexterity = Addon(
            profile_id="plone.app.dexterity:default", check_module="no.such.module"
        )
        # non-existing one:
        foo = Addon(profile_id="foo")
        addonlist = AddonList([cmfeditions, discussion, dexterity, foo])
        # Calling it should give no errors.
        addonlist.upgrade_all(self.portal)

        # Get the last CMFEditions profile version, as that will be
        # the only one that gets upgraded during the second upgrade.
        setup = getToolByName(self.portal, "portal_setup")
        cmfeditions_version = setup.getLastVersionForProfile(cmfeditions.profile_id)

        # Now mess with the profile versions.
        setup.setLastVersionForProfile(cmfeditions.profile_id, "2.0")
        setup.setLastVersionForProfile(dexterity.profile_id, "0.1")
        # 'unknown' needs special handling, otherwise the version will
        # become a tuple ('unknown',):
        setup._profile_upgrade_versions[discussion.profile_id] = "unknown"

        # Run the upgrade again.
        addonlist.upgrade_all(self.portal)

        # Check the profile versions.
        # CMFEditions should be the last one:
        self.assertEqual(
            setup.getLastVersionForProfile(cmfeditions.profile_id), cmfeditions_version
        )
        # We had set discussion to unknown, so it will not have been
        # upgraded:
        self.assertEqual(
            setup.getLastVersionForProfile(discussion.profile_id), "unknown"
        )
        # We had given dexterity a failing check_module, so it will
        # not have been upgraded:
        self.assertEqual(
            setup.getLastVersionForProfile(dexterity.profile_id), ("0", "1")
        )
        # The foo profile never existed:
        self.assertEqual(setup.getLastVersionForProfile(foo.profile_id), "unknown")

    def test_plone_addonlist_upgrade_all(self):
        # Test the actual filled addon list.
        from Products.CMFPlone.MigrationTool import ADDON_LIST

        # Several addons did not get fully upgraded in the past, which
        # is why this list was created.
        cmfeditions_id = "Products.CMFEditions:CMFEditions"
        discussion_id = "plone.app.discussion:default"
        querystring_id = "plone.app.querystring:default"
        # Note the current versions.
        setup = getToolByName(self.portal, "portal_setup")
        getversion = setup.getLastVersionForProfile
        cmfeditions_version = getversion(cmfeditions_id)
        discussion_version = getversion(discussion_id)
        querystring_version = getversion(querystring_id)
        # Check that they are not unknown
        self.assertNotEqual(cmfeditions_version, "unknown")
        self.assertNotEqual(discussion_version, "unknown")
        self.assertNotEqual(querystring_version, "unknown")
        # So let's mess with some profile versions.  We get some older
        # versions that really exist.
        setversion = setup.setLastVersionForProfile
        setversion(cmfeditions_id, "2.0")
        setversion(discussion_id, "100")
        setversion(querystring_id, "7")
        # Check that it worked, that the profile versions really are
        # different.
        self.assertNotEqual(cmfeditions_version, getversion(cmfeditions_id))
        self.assertNotEqual(discussion_version, getversion(discussion_id))
        self.assertNotEqual(querystring_version, getversion(querystring_id))

        # Run the upgrade.
        ADDON_LIST.upgrade_all(self.portal)

        # Check that it worked, that the profiles are now at their
        # original versions.
        self.assertEqual(cmfeditions_version, getversion(cmfeditions_id))
        self.assertEqual(discussion_version, getversion(discussion_id))
        self.assertEqual(querystring_version, getversion(querystring_id))
