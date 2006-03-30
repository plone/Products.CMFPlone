#
# Tests the ControlPanel
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneControlPanel import PloneControlPanel, \
                                                default_configlets


class TestControlPanel(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.controlpanel = self.portal.portal_controlpanel
        # get the expected default groups and configlets
        self.defaultgroups = [g.split('|')[1] for g in PloneControlPanel.groups]
        self.defaultconfiglets = [conf['appId'] for conf in default_configlets]

    def testDefaultGroups(self):
        for group in self.defaultgroups:
            self.failUnless(group in self.controlpanel.getGroupIds(),
                            "Missing group with id '%s'" % group)

    def testDefaultConfiglets(self):

        for id in self.defaultconfiglets:
            self.failUnless(id in [conf.getAppId()
                               for conf in self.controlpanel.listActions()],
                            "Missing configlet with appId '%s'" % id)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestControlPanel))
    return suite

if __name__ == '__main__':
    framework()
