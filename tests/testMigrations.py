#
# Tests for migration components
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.migrations.v2.two04_two05 import replaceFolderPropertiesWithEdit
from Products.CMFPlone.migrations.v2.two04_two05 import interchangeEditAndSharing
from Products.CMFPlone.migrations.v2.two04_two05 import addFolderListingActionToTopic

from Products.CMFPlone.migrations.v2_1.alphas import addFullScreenAction
from Products.CMFPlone.migrations.v2_1.alphas import addFullScreenActionIcon


class MigrationTest(PloneTestCase.PloneTestCase):

    def removeActionFromType(self, type_name, action_id):
        # Removes an action from a portal type
        info = self.types.getTypeInfo(type_name)
        typeob = getattr(self.types, info.getId())
        actions = info.listActions()
        actions = [x for x in actions if x.id != action_id]
        typeob._actions = tuple(actions)

    def removeActionFromTool(self, action_id):
        # Removes an action from portal_actions
        tool = getattr(self.portal, 'portal_actions')
        actions = tool.listActions()
        actions = [x for x in actions if x.id != action_id]
        tool._actions = tuple(actions)

    def removeActionIconFromTool(self, action_id):
        # Removes an action icon from portal_actionicons
        tool = getattr(self.portal, 'portal_actionicons')
        try:
            tool.removeActionIcon('plone', action_id)
        except KeyError:
            pass # No icon associated


class TestMigrations_v2(MigrationTest):

    def afterSetUp(self):
        self.types = self.portal.portal_types

    def testReplaceFolderPropertiesWithEditNoFolder(self):
        # Should not fail if Folder type is missing
        self.types._delObject('Folder')
        replaceFolderPropertiesWithEdit(self.portal, [])

    def testReplaceFolderPropertiesWithEditNoEdit(self):
        # Should not fail if action is missing
        self.removeActionFromType('Folder', 'edit')
        replaceFolderPropertiesWithEdit(self.portal, [])

    def testInterchangeEditAndSharingNoFolder(self):
        # Should not fail if Folder type is missing
        self.types._delObject('Folder')
        interchangeEditAndSharing(self.portal, [])

    def testInterchangeEditAndSharingNoSharing(self):
        # Should not fail if action is missing
        self.removeActionFromType('Folder', 'local_roles')
        interchangeEditAndSharing(self.portal, [])

    def testInterchangeEditAndSharingNoEdit(self):
        # Should not fail if action is missing
        self.removeActionFromType('Folder', 'edit')
        interchangeEditAndSharing(self.portal, [])

    def testAddFolderListingToTopicNoTopic(self):
        # Should not fail if Topic type is missing
        self.types._delObject('Topic')
        addFolderListingActionToTopic(self.portal, [])


class TestMigrations_v2_1(MigrationTest):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions
        self.icons = self.portal.portal_actionicons

    def testAddFullScreenAction(self):
        # Should add the full_screen action
        self.removeActionFromTool('full_screen')
        addFullScreenAction(self.portal, [])
        self.failUnless('full_screen' in [x.id for x in self.actions.listActions()])

    def testAddFullScreenActionTwice(self):
        # Should not fail if migrated again
        self.removeActionFromTool('full_screen')
        addFullScreenAction(self.portal, [])
        addFullScreenAction(self.portal, [])
        self.failUnless('full_screen' in [x.id for x in self.actions.listActions()])

    def testAddFullScreenActionNoTool(self):
        # Should not fail if portal_actions is missing
        self.portal._delObject('portal_actions')
        addFullScreenAction(self.portal, [])

    def testAddFullScreenActionIcon(self):
        # Should add the full_screen action icon
        self.removeActionIconFromTool('full_screen')
        addFullScreenActionIcon(self.portal, [])
        self.failUnless('full_screen' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddFullScreenActionIconTwice(self):
        # Should not fail if migrated again
        self.removeActionIconFromTool('full_screen')
        addFullScreenActionIcon(self.portal, [])
        addFullScreenActionIcon(self.portal, [])
        self.failUnless('full_screen' in [x.getActionId() for x in self.icons.listActionIcons()])

    def testAddFullScreenActionIcon(self):
        # Should not fail if portal_actionicons is missing
        self.portal._delObject('portal_actionicons')
        addFullScreenActionIcon(self.portal, [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations_v2))
    suite.addTest(makeSuite(TestMigrations_v2_1))
    return suite

if __name__ == '__main__':
    framework()
