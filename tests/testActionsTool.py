#
# ActionsTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from cStringIO import StringIO
import traceback
from sets import Set

expected_filtered_actions=Set(['site_actions', 'object', 'workflow', 'portal_tabs', 'global', 'batch', 'object_buttons', 'document_actions', 'user', 'folder_buttons', 'folder'])

class TestActionsTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.actions = self.portal.portal_actions

    def fail_tb(self, msg):
        """ special fail for capturing errors """
        out = StringIO()
        t, e, tb = sys.exc_info()
        traceback.print_exc(tb, out)
        self.fail("%s\n %s\n %s\n %s\n" %( msg, t, e,  out.getvalue()) )

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

    def testListFilteredActionsFor(self):
        self.assertEqual(Set(self.actions.listFilteredActionsFor(self.folder).keys()),
                         expected_filtered_actions)

    def testMissingActionProvider(self):
        self.portal._delObject('portal_registration')
        try:
            self.actions.listFilteredActionsFor(self.folder)
        except :
            self.fail_tb('Should not bomb out if a provider is missing')

    def testBrokenActionProvider(self):
        self.portal.portal_registration = None
        try:
            self.actions.listFilteredActionsFor(self.folder)
        except :
            self.fail_tb('Should not bomb out if a provider is broken')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestActionsTool))
    return suite

if __name__ == '__main__':
    framework()
