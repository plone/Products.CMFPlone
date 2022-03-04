from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING

import unittest


class TestControlPanel(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.controlpanel = self.layer['portal'].portal_controlpanel

        # get the expected default groups and configlets
        self.groups = ['Plone', 'Products']
        self.configlets = ['QuickInstaller', 'MailHost',
                           'UsersGroups', 'PortalSkin',
                           'ZMI', 'SecuritySettings',
                           'NavigationSettings', 'SearchSettings',
                           'errorLog', 'PloneReconfig', 'TypesSettings',
                           'FilterSettings',
                           'Maintenance']

    def testDefaultGroups(self):
        for group in self.groups:
            self.assertTrue(group in self.controlpanel.getGroupIds(),
                            "Missing group with id '%s'" % group)

    def testDefaultConfiglets(self):
        for title in self.configlets:
            self.assertTrue(title in [a.getAction(self)['id']
                                      for a in self.controlpanel.listActions()],
                            "Missing configlet with id '%s'" % title)
