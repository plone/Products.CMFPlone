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

class TestMigrations(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.types = self.portal.portal_types

    def removeAction(self, type_name, action_id):
        info = self.types.getTypeInfo(type_name)
        typeob = getattr(self.types, info.getId())
        actions = info._cloneActions()
        actions = [x for x in actions if x.id != action_id]
        typeob._actions = tuple(actions)

    def testReplaceFolderPropertiesWithEditNoFolder(self):
        # Should not fail if Folder type is missing
        self.types._delObject('Folder')
        replaceFolderPropertiesWithEdit(self.portal, [])

    def testReplaceFolderPropertiesWithEditNoEdit(self):
        # Should not fail if action is missing
        self.removeAction('Folder', 'edit')
        replaceFolderPropertiesWithEdit(self.portal, [])

    def testInterchangeEditAndSharingNoFolder(self):
        # Should not fail if Folder type is missing
        self.types._delObject('Folder')
        interchangeEditAndSharing(self.portal, [])

    def testInterchangeEditAndSharingNoSharing(self):
        # Should not fail if action is missing
        self.removeAction('Folder', 'local_roles')
        interchangeEditAndSharing(self.portal, [])

    def testInterchangeEditAndSharingNoEdit(self):
        # Should not fail if action is missing
        self.removeAction('Folder', 'edit')
        interchangeEditAndSharing(self.portal, [])

    def testAddFolderListingToTopicNoTopic(self):
        # Should not fail if Topic type is missing
        self.types._delObject('Topic')
        addFolderListingActionToTopic(self.portal, [])

    # 2.1 alpha 1 tests
    
    def testAddNonDefaultPageTypesProperty(self):
        # Ensure we now have the non_default_page_types property
        siteprops = self.portal.portal_properties.site_properties
        self.failUnlessEqual(siteprops.getProperty('non_default_page_types', ()),
                             ('Folder', 'Large Plone Folder', 'Image', 'File'))
                                

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations))
    return suite

if __name__ == '__main__':
    framework()
