#
# ActionsTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase


class TestActionsTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions

    def testAddAction(self):
        # addAction should work even though PloneTestCase patches _cloneActions
        action_infos = self.actions.listActions()
        length = len(action_infos)
        self.actions.addAction(id='foo',
                               name='foo_name',
                               action='foo_action',
                               condition='foo_condition',
                               permission='foo_permission',
                               category='foo_category',
                               visible=1)
        action_infos = self.actions.listActions()
        self.assertEqual(len(action_infos), length + 1)
        self.assertEqual(action_infos[-1].id, 'foo')
        self.assertEqual(action_infos[-1].title, 'foo_name')
        self.assertEqual(action_infos[-1].permissions, ('foo_permission',))
        self.assertEqual(action_infos[-1].category, 'foo_category')


if __name__ == '__main__':
    framework()
else:
    def test_suite():
        from unittest import TestSuite, makeSuite
        suite = TestSuite()
        suite.addTest(makeSuite(TestActionsTool))
        return suite
