#
# MigrationTool tests
#

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
        self.failIf(self.migration.needUpgrading(),
                    'Migration needs upgrading')

    def testMigrationNeedsUpdateRole(self):
        self.failIf(self.migration.needUpdateRole(),
                    'Migration needs role update')

    def testMigrationNeedsRecatalog(self):
        self.failIf(self.migration.needRecatalog(),
                    'Migration needs recataloging')

    def testListUpgradeSteps(self):
        # There should be no upgrade steps from the current version
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.failUnless(len(upgrades) == 0)

    def testDoUpgrades(self):
        self.setRoles(['Manager'])

        self.setup.setLastVersionForProfile(_DEFAULT_PROFILE, '2.5')
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.failUnless(len(upgrades) > 0)

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
        self.assertEquals(last, current)

        # There are no more upgrade steps available
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.failUnless(len(upgrades) == 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrationTool))
    return suite
