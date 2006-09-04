#
# MigrationTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase


class TestMigrationTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.migration = self.portal.portal_migration

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

    def testForceMigrationFromUnsupportedVersion(self):
        version = '2.0.5'
        while version is not None:
            version, msg = self.migration._upgrade(version)
        expect = 'Migration stopped at version 2.0.5.'
        self.assertEqual(msg[0], expect)

    def testForceMigration(self):
        self.setRoles(['Manager'])
        # Make sure we don't embarrass ourselves again...
        version = '2.1'
        # XXX This fails because when migrating old sites we still have
        # ActionInformation objects stored in the actions tool.
        # We need to write a migration that converts these to Actions
        # before any other migration step is run
        while version is not None:
            version, msg = self.migration._upgrade(version)
        expect = 'Migration completed at version %s.' % \
                 self.migration.getFileSystemVersion()
        self.assertEqual(msg[0], expect)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrationTool))
    return suite

if __name__ == '__main__':
    framework()
