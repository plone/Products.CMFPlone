#
# QuickInstallerTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase


class TestQuickInstallerTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller

    def _installed(self):
        return [p['id'] for p in self.qi.listInstalledProducts()]

    def _available(self):
        return [p['id'] for p in self.qi.listInstallableProducts()]

    def testInstallUninstallProduct(self):
        # CMFFormController should be uninstalled, we install it and
        # it should not show up as installable
        self.setRoles(('Manager',))
        self.qi.CMFFormController.locked = 0
        self.qi.uninstallProducts(['CMFFormController',])
        self.failIf('CMFFormController' in self._installed())
        self.failUnless('CMFFormController' in self._available())
        self.qi.installProduct('CMFFormController')
        self.failIf('CMFFormController' in self._available())
        self.failUnless('CMFFormController' in self._installed())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestQuickInstallerTool))
    return suite

if __name__ == '__main__':
    framework()
