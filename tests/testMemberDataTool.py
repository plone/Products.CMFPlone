#
# MemberDataTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from OFS.Image import Image
default_user = PloneTestCase.default_user


class TestMemberDataTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.memberdata = self.portal.portal_memberdata

    def testSetPortrait(self):
        self.memberdata._setPortrait(Image(id=default_user, file=dummy.File(), title=''), default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user).getId(), default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user).meta_type, 'Image')

    def testDeletePortrait(self):
        self.memberdata._setPortrait(Image(id=default_user, file=dummy.File(), title=''), default_user)
        self.memberdata._deletePortrait(default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user), None)

    def testPruneMemberDataContents(self):
        # Only test what is not already tested elswhere
        self.memberdata._setPortrait(Image(id=default_user, file=dummy.File(), title=''), default_user)
        self.memberdata._setPortrait(Image(id=default_user, file=dummy.File(), title=''), 'dummy')
        self.memberdata.pruneMemberDataContents()
        self.assertEqual(len(self.memberdata.portraits.objectIds()), 1)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMemberDataTool))
    return suite

if __name__ == '__main__':
    framework()
