#
# MemberDataTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

default_user = PloneTestCase.default_user


from OFS.Image import Image
# Fake upload object
class Portrait:
    filename = 'foo.gif'
    def seek(*args): pass
    def tell(*args): return 0
    def read(*args): return 'bar'


class TestMemberDataTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.memberdata = self.portal.portal_memberdata

    def testSetPortrait(self):
        self.memberdata._setPortrait(Image(id=default_user, file=Portrait(), title=''), default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user).getId(), default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user).meta_type, 'Image')

    def testDeletePortrait(self):
        self.memberdata._setPortrait(Image(id=default_user, file=Portrait(), title=''), default_user)
        self.memberdata._deletePortrait(default_user)
        self.assertEqual(self.memberdata._getPortrait(default_user), None)

    def testPruneMemberDataContents(self):
        # Only test what is not already tested elswhere
        self.memberdata._setPortrait(Image(id=default_user, file=Portrait(), title=''), default_user)
        self.memberdata._setPortrait(Image(id=default_user, file=Portrait(), title=''), 'dummy')
        self.memberdata.pruneMemberDataContents()
        self.assertEqual(len(self.memberdata.portraits.objectIds()), 1)


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestMemberDataTool))
        return suite

