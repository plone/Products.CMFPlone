#
# QuickInstallerTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Acquisition import aq_base


class TestQuickInstallerTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.qi = self.portal.portal_quickinstaller

    def _installed(self):
        return [p['id'] for p in self.qi.listInstalledProducts()]
    def _available(self):
        return [p['id'] for p in self.qi.listInstallableProducts()]

    def testInstallUninstallProduct(self):
        '''CMFFormController should be uninstalled, we install it and it should not show up as installable'''
        self.qi.uninstallProducts(['CMFFormController',])
        assert 'CMFFormController' not in self._installed()
        assert 'CMFFormController' in self._available()
        self.qi.installProduct('CMFFormController')
        assert 'CMFFormController' not in self._available()
        
    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestQuickInstallerTool))
        return suite

