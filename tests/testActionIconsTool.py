#
# ActionIconsTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase


class TestActionIconsTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.actionicons = self.portal.portal_actionicons

    def testAddActionIcon(self):
        length = len(self.actionicons.listActionIcons())
        self.actionicons.addActionIcon('content_actions',
                                       'preview',
                                       'plone_images/lock_icon.gif',
                                       title='preview')
        action_icons=self.actionicons.listActionIcons()
        preview=action_icons[-1]
        self.assertEqual(len(action_icons), length+1)
        self.assertEqual(preview._category, 'content_actions')
        self.assertEqual(preview._action_id, 'preview')
        self.assertEqual(preview._title, 'preview')

    def testRenderActionIcon(self):
        self.testAddActionIcon()
        icon=self.actionicons.renderActionIcon('content_actions',
                                               'preview')
        obj=self.portal.restrictedTraverse('plone_images/lock_icon.gif')
        self.assertEqual(obj, icon)

    def testRenderDefaultActionIcon(self):
        icon=self.actionicons.renderActionIcon('content_actions',
                                               'doesnotexist',
                                               default='document_icon.gif')
        obj=self.portal.restrictedTraverse('plone_images/document_icon.gif')
        self.assertEqual(obj, icon)

    def testRenderNoneActionIcon(self):
        icon=self.actionicons.renderActionIcon('content_actions',
                                               'doesnotexist',
                                               None)
        self.assertEqual(icon, None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestActionIconsTool))
    return suite

if __name__ == '__main__':
    framework()
