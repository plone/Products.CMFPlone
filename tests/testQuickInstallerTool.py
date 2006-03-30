#
# QuickInstallerTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase


class InstanceHomeFixup:
    '''Sigh, in Zope versions < 2.7.1 the Testing package changes
       the INSTANCE_HOME variable. QuickInstaller now requires a 
       valid INSTANCE_HOME so we have to restore it.
    '''

    from Globals import package_home
    from Products.CMFPlone.tests import GLOBALS
    PACKAGE_HOME = package_home(GLOBALS)

    instance_home = os.path.join(PACKAGE_HOME, os.pardir, os.pardir, os.pardir)
    instance_home = os.path.abspath(instance_home)

    if os.path.exists(os.path.join(instance_home, 'Products')):
        # We may be installed below SOFTWARE_HOME
        d, e = os.path.split(instance_home)
        if e == 'python':
            d, e = os.path.split(d)
            if e == 'lib':
                instance_home = d
    if not os.path.exists(os.path.join(instance_home, 'Products')):
        instance_home = '' # punt

    def afterSetUp(self):
        builtins = getattr(__builtins__, '__dict__', __builtins__)
        if self.instance_home:
            self._saved = INSTANCE_HOME
            builtins['INSTANCE_HOME'] = self.instance_home

    def afterClear(self):
        builtins = getattr(__builtins__, '__dict__', __builtins__)
        if hasattr(self, '_saved'):
            builtins['INSTANCE_HOME'] = self._saved


class TestQuickInstallerTool(InstanceHomeFixup, PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        InstanceHomeFixup.afterSetUp(self)
        self.qi = self.portal.portal_quickinstaller

    def _installed(self):
        return [p['id'] for p in self.qi.listInstalledProducts()]

    def _available(self):
        return [p['id'] for p in self.qi.listInstallableProducts()]

    def testInstallUninstallProduct(self):
        # CMFFormController should be uninstalled, we install it and
        # it should not show up as installable
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
