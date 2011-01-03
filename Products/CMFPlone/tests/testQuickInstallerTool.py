#
# QuickInstallerTool tests
#

from Products.CMFPlone.tests import PloneTestCase


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
        self.failUnless('CMFPlacefulWorkflow' in self._installed())
        self.failIf('CMFPlacefulWorkflow' in self._available())
        self.qi.uninstallProducts(['CMFPlacefulWorkflow', ])
        self.failUnless('CMFPlacefulWorkflow' in self._available())
        self.failIf('CMFPlacefulWorkflow' in self._installed())

    def testUpgradeProfilesNotShown(self):
        self.failIf('plone.app.upgrade.v30' in self._available())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestQuickInstallerTool))
    return suite
