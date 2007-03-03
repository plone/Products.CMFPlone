#
# Tests the ControlPanel
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.component import getUtility

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.interfaces import IControlPanel


class TestControlPanel(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.controlpanel = getUtility(IControlPanel)
        
        # get the expected default groups and configlets
        self.groups     = ['Plone', 'Products', 'Member']
        self.configlets = ['QuickInstaller', 'portal_atct', 'MailHost',
                           'UsersGroups', 'MemberPrefs', 'PortalSkin',
                           'MemberPassword', 'ZMI', 'SecuritySettings',
                           'NavigationSettings', 'SearchSettings',
                           'errorLog', 'kupu', 'PloneReconfig',
                           'CalendarSettings', 'TypesSettings', 
                           'PloneLanguageTool', 'CalendarSettings',
                           'HtmlFilter', 'Maintenance']

    def testDefaultGroups(self):
        for group in self.groups:
            self.failUnless(group in self.controlpanel.getGroupIds(),
                            "Missing group with id '%s'" % group)

    def testDefaultConfiglets(self):
        for title in self.configlets:
            self.failUnless(title in [a.getAction(self)['id']
                                   for a in self.controlpanel.listActions()],
                            "Missing configlet with id '%s'" % title)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestControlPanel))
    return suite

if __name__ == '__main__':
    framework()
