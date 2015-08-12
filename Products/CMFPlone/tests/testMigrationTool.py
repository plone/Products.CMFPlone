from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFCore.utils import getToolByName


class TestMigrationTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.migration = getToolByName(self.portal, "portal_migration")
        self.setup = getToolByName(self.portal, "portal_setup")

    def testMigrationFinished(self):
        self.assertEqual(self.migration.getInstanceVersion(),
                         self.migration.getFileSystemVersion(),
                         'Migration failed')

    def testMigrationNeedsUpgrading(self):
        self.assertFalse(self.migration.needUpgrading(),
                    'Migration needs upgrading')

    def testMigrationNeedsUpdateRole(self):
        self.assertFalse(self.migration.needUpdateRole(),
                    'Migration needs role update')

    def testMigrationNeedsRecatalog(self):
        self.assertFalse(self.migration.needRecatalog(),
                    'Migration needs recataloging')

    def testListUpgradeSteps(self):
        # There should be no upgrade steps from the current version
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertTrue(len(upgrades) == 0)

    def testDoUpgrades(self):
        self.setRoles(['Manager'])

        self.setup.setLastVersionForProfile(_DEFAULT_PROFILE, '2.5')
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertTrue(len(upgrades) > 0)

        request = self.portal.REQUEST
        request.form['profile_id'] = _DEFAULT_PROFILE

        steps = []
        for u in upgrades:
            if isinstance(u, list):
                steps.extend([s['id'] for s in u])
            else:
                steps.append(u['id'])

        request.form['upgrades'] = steps
        self.setup.manage_doUpgrades(request=request)

        # And we have reached our current profile version
        current = self.setup.getVersionForProfile(_DEFAULT_PROFILE)
        current = tuple(current.split('.'))
        last = self.setup.getLastVersionForProfile(_DEFAULT_PROFILE)
        self.assertEqual(last, current)

        # There are no more upgrade steps available
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertTrue(len(upgrades) == 0)

    def testUpgrade(self):
        self.setRoles(['Manager'])
        self.setup.setLastVersionForProfile(_DEFAULT_PROFILE, '2.5')
        self.migration.upgrade()

        # And we have reached our current profile version
        current = self.setup.getVersionForProfile(_DEFAULT_PROFILE)
        current = tuple(current.split('.'))
        last = self.setup.getLastVersionForProfile(_DEFAULT_PROFILE)
        self.assertEqual(last, current)

        # There are no more upgrade steps available
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertTrue(len(upgrades) == 0)


class TestAddonList(PloneTestCase.PloneTestCase):

    def test_addon_safe(self):
        from Products.CMFPlone.MigrationTool import Addon
        addon = Addon(profile_id=_DEFAULT_PROFILE)
        self.assertTrue(addon.safe())
        addon = Addon(profile_id=_DEFAULT_PROFILE,
                      check_module='Products.CMFPlone')
        self.assertTrue(addon.safe())
        addon = Addon(profile_id=_DEFAULT_PROFILE,
                      check_module='Products.CMFPlone.foobarbaz')
        self.assertFalse(addon.safe())

    def test_addon_repr(self):
        from Products.CMFPlone.MigrationTool import Addon
        addon = Addon(profile_id='foo')
        self.assertEqual(repr(addon), u'<Addon profile foo>')
        self.assertEqual(str(addon), '<Addon profile foo>')

    def test_upgrade_all(self):
        from Products.CMFPlone.MigrationTool import Addon
        from Products.CMFPlone.MigrationTool import AddonList
        # real ones:
        cmfeditions = Addon(profile_id=u'Products.CMFEditions:CMFEditions')
        discussion = Addon(profile_id=u'plone.app.discussion:default')
        # real one with failing check_module:
        dexterity = Addon(profile_id=u'plone.app.dexterity:default',
                          check_module='no.such.module')
        # non-existing one:
        foo = Addon(profile_id='foo')
        addonlist = AddonList([
            cmfeditions,
            discussion,
            dexterity,
            foo
            ])
        # Calling it should give no errors.
        addonlist.upgrade_all(self.portal)

        # Get the last CMFEditions profile version, as that will be
        # the only one that gets upgraded during the second upgrade.
        setup = getToolByName(self.portal, "portal_setup")
        cmfeditions_version = setup.getLastVersionForProfile(
            cmfeditions.profile_id)

        # Now mess with the profile versions.
        setup.setLastVersionForProfile(cmfeditions.profile_id, '2.0')
        setup.setLastVersionForProfile(dexterity.profile_id, '0.1')
        # 'unknown' needs special handling, otherwise the version will
        # become a tuple ('unknown',):
        setup._profile_upgrade_versions[discussion.profile_id] = 'unknown'

        # Run the upgrade again.
        addonlist.upgrade_all(self.portal)

        # Check the profile versions.
        # CMFEditions should be the last one:
        self.assertEqual(
            setup.getLastVersionForProfile(cmfeditions.profile_id),
            cmfeditions_version)
        # We had set discussion to unknown, so it will not have been
        # upgraded:
        self.assertEqual(
            setup.getLastVersionForProfile(discussion.profile_id),
            'unknown')
        # We had given dexterity a failing check_module, so it will
        # not have been upgraded:
        self.assertEqual(
            setup.getLastVersionForProfile(dexterity.profile_id),
            ('0', '1'))
        # The foo profile never existed:
        self.assertEqual(
            setup.getLastVersionForProfile(foo.profile_id),
            'unknown')

    def test_plone_addonlist_upgrade_all(self):
        # Test the actual filled addon list.
        from Products.CMFPlone.MigrationTool import ADDON_LIST
        # Several addons did not get fully upgraded in the past, which
        # is why this list was created.
        cmfeditions_id = 'Products.CMFEditions:CMFEditions'
        discussion_id = 'plone.app.discussion:default'
        jq_id = 'plone.app.jquery:default'
        jqtools_id = 'plone.app.jquerytools:default'
        sunburst_id = 'plonetheme.sunburst:default'
        # Note the current versions.
        setup = getToolByName(self.portal, "portal_setup")
        getversion = setup.getLastVersionForProfile
        cmfeditions_version = getversion(cmfeditions_id)
        discussion_version = getversion(discussion_id)
        jq_version = getversion(jq_id)
        jqtools_version = getversion(jqtools_id)
        sunburst_version = getversion(sunburst_id)
        # So let's mess with some profile versions.  We get some older
        # versions that really exist.
        setversion = setup.setLastVersionForProfile
        setversion(cmfeditions_id, '2.0')
        setversion(discussion_id, '100')
        setversion(jq_id, '2')
        setversion(jqtools_id, '1.0rc2')
        setversion(sunburst_id, '2')
        # Check that it worked, that the profile versions really are
        # different.
        self.assertNotEqual(cmfeditions_version, getversion(cmfeditions_id))
        self.assertNotEqual(discussion_version, getversion(discussion_id))
        self.assertNotEqual(jq_version, getversion(jq_id))
        self.assertNotEqual(jqtools_version, getversion(jqtools_id))
        self.assertNotEqual(sunburst_version, getversion(sunburst_id))

        # Run the upgrade.
        ADDON_LIST.upgrade_all(self.portal)

        # Check that it worked, that the profiles are now at their
        # original versions.
        self.assertEqual(cmfeditions_version, getversion(cmfeditions_id))
        self.assertEqual(discussion_version, getversion(discussion_id))
        self.assertEqual(jq_version, getversion(jq_id))
        self.assertEqual(jqtools_version, getversion(jqtools_id))
        self.assertEqual(sunburst_version, getversion(sunburst_id))
