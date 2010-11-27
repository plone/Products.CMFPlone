#
# Tests the ControlPanel
#


from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests import PloneTestCase


class TestControlPanel(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")

        # get the expected default groups and configlets
        self.groups     = ['Plone', 'Products']
        self.configlets = ['QuickInstaller', 'portal_atct', 'MailHost',
                           'UsersGroups', 'MemberPrefs', 'PortalSkin',
                           'MemberPassword', 'ZMI', 'SecuritySettings',
                           'NavigationSettings', 'SearchSettings',
                           'errorLog', 'PloneReconfig',
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
