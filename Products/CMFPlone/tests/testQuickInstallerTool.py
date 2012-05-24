from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone import tests
from Products.Five import zcml
from Products.Five import fiveconfigure


class TestQuickInstallerTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller

    def _installed(self):
        return [p['id'] for p in self.qi.listInstalledProducts()]

    def _available(self):
        return [p['id'] for p in self.qi.listInstallableProducts()]

    def testInstallUninstallProduct(self):
        try:
            import Products.CMFPlacefulWorkflow
        except ImportError:
            return
        # CMFPlacefulWorkflow should be uninstalled, we install it and
        # it should not show up as installable
        self.setRoles(('Manager',))
        self.qi.installProducts(['CMFPlacefulWorkflow', ])
        self.assertTrue('CMFPlacefulWorkflow' in self._installed())
        self.assertFalse('CMFPlacefulWorkflow' in self._available())
        self.qi.uninstallProducts(['CMFPlacefulWorkflow', ])
        self.assertTrue('CMFPlacefulWorkflow' in self._available())
        self.assertFalse('CMFPlacefulWorkflow' in self._installed())

    def testUpgradeProfilesNotShown(self):
        self.assertFalse('plone.app.upgrade.v30' in self._available())

    def testLatestUpgradeProfiles(self):
        self._load_zcml('test_upgrades1.zcml')
        latest = self.qi.getLatestUpgradeStep('Products.CMFPlone:testfixture')
        self.assertTrue(latest == '3')

    def testLatestUpgradeProfiles2(self):
        # make sure strings don't break things
        # note that pkg_resources interprets 1 as
        # ''00000001', which is > 'banana'
        self._load_zcml('test_upgrades2.zcml')
        latest = self.qi.getLatestUpgradeStep('Products.CMFPlone:testfixture')
        self.assertTrue(latest == '3')

    def _load_zcml(self, filename):
        fiveconfigure.debug_mode = True
        zcml.load_config(filename, package=tests)
        fiveconfigure.debug_mode = False


def dummy_handler():
    pass
