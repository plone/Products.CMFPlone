#
# Tests the PloneTool
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

default_user = PloneTestCase.default_user


class TestPloneTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.utils = self.portal.plone_utils
        self.membership = self.portal.portal_membership
        self.membership.addMember('new_owner', 'secret', ['Member'], [])

    def testChangeOwnershipOf(self):
        self.folder.invokeFactory('Document', 'doc')
        doc = self.folder.doc
        self.assertEqual(doc.Creator(), default_user)
        self.assertEqual(doc.get_local_roles_for_userid(default_user), ('Owner',))

        self.utils.changeOwnershipOf(doc, 'new_owner')
        self.assertEqual(doc.Creator(), 'new_owner')
        self.assertEqual(doc.get_local_roles_for_userid('new_owner'), ('Owner',))

        # Initial creator no longer has Owner role.
        self.assertEqual(doc.get_local_roles_for_userid(default_user), ())


if __name__ == '__main__':
    framework()
else:
    # While framework.py provides its own test_suite()
    # method the testrunner utility does not.
    from unittest import TestSuite, makeSuite
    def test_suite():
        suite = TestSuite()
        suite.addTest(makeSuite(TestPloneTool))
        return suite
