#
# MembershipTool tests
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
_user_role = 'Member'


class TestMembershipTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.mt = self.portal.portal_membership

    def testGetPersonalFolder(self):
        '''Should return the .personal folder'''
        personal = getattr(self.folder, self.mt.personal_id, None)
        assert personal is not None
        assert self.mt.getPersonalFolder(_user_name) == personal
         
    def testGetPersonalFolderIfMissing(self):
        '''Should return None as the .personal folder is missing'''
        self.folder._delObject(self.mt.personal_id)
        assert self.mt.getPersonalFolder(_user_name) is None       

    def testGetPersonalFolderIfNoHome(self):
        '''Should return None as the user has no home folder'''
        members = self.mt.getMembersFolder()
        members._delObject(_user_name)
        assert self.mt.getPersonalFolder(_user_name) is None       


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestMembershipTool))
        return suite

