#
# MemberDataTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

# Create a Plone site in the test (demo-) storage
app = ZopeTestCase.app()
PloneTestCase.setupPloneSite(app, id='portal')
ZopeTestCase.close(app)

_user_name = ZopeTestCase._user_name

from OFS.Image import Image
# Fake upload object
class Portrait:
    filename = 'foo.gif'
    def seek(*args): pass
    def tell(*args): return 0
    def read(*args): return 'bar'


class TestMemberDataTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.pm = self.portal.portal_memberdata

    def testSetPortrait(self):
        self.pm._setPortrait(Image(id=_user_name, file=Portrait(), title=''), _user_name)
        assert self.pm._getPortrait(_user_name).getId() == _user_name
        assert self.pm._getPortrait(_user_name).meta_type == 'Image'

    def testPruneMemberDataContents(self):
        # Only test what is not already tested elswhere
        self.pm._setPortrait(Image(id=_user_name, file=Portrait(), title=''), _user_name)
        self.pm._setPortrait(Image(id=_user_name, file=Portrait(), title=''), 'dummy')
        self.pm.pruneMemberDataContents()
        assert len(self.pm.portraits.objectIds()) == 1


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestMemberDataTool))
        return suite

