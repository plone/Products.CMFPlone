#
# Tests for migration components
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.migrations.v2.two04_two05 import interchangeEditAndSharing


class TestMigrations(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.types = self.portal.portal_types

    def removeAction(self, type_name, action_id):
        info = self.types.getTypeInfo(type_name)
        typeob = getattr(self.types, info.getId())
        actions = info._cloneActions()
        actions = [x for x in actions if x.id != action_id]
        typeob._actions = tuple(actions)

    def testInterchangeEditAndSharing_1(self):
        # Should not bomb out if action is missing
        self.removeAction('Folder', 'local_roles')
        interchangeEditAndSharing(self.portal, [])

    def testInterchangeEditAndSharing_2(self):
        # Should not bomb out if action is missing
        self.removeAction('Folder', 'edit')
        interchangeEditAndSharing(self.portal, [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMigrations))
    return suite

if __name__ == '__main__':
    framework()
