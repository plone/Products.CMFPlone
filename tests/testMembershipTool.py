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


# Fake upload object
class Portrait:
    filename = 'foo.gif'
    def seek(*args): pass
    def tell(*args): return 0
    def read(*args): return 'bar'


class TestMembershipTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.pm = self.portal.portal_membership

    def testGetPersonalFolder(self):
        '''Should return the .personal folder'''
        personal = getattr(self.folder, self.pm.personal_id, None)
        assert personal is not None
        assert self.pm.getPersonalFolder(_user_name) == personal
         
    def testGetPersonalFolderIfMissing(self):
        '''Should return None as the .personal folder is missing'''
        self.folder._delObject(self.pm.personal_id)
        assert self.pm.getPersonalFolder(_user_name) is None       

    def testGetPersonalFolderIfNoHome(self):
        '''Should return None as the user has no home folder'''
        members = self.pm.getMembersFolder()
        members._delObject(_user_name)
        assert self.pm.getPersonalFolder(_user_name) is None       

    def testGetPersonalPortrait(self):
        '''Should return the default portrait'''
        assert self.pm.getPersonalPortrait(_user_name).getId() == 'defaultUser.gif'

    def testChangeMemberPortrait(self):
        '''Should change the portrait image'''
        self.pm.changeMemberPortrait(Portrait(), _user_name)
        assert self.pm.getPersonalPortrait(_user_name).getId() == _user_name
        assert self.pm.getPersonalPortrait(_user_name).meta_type == 'Image'

    def testGetPersonalPortraitUsesRequestVar(self):
        '''Should use the request var if member_id is not given'''
        self.pm.changeMemberPortrait(Portrait(), 'user_2')
        assert self.pm.getPersonalPortrait(None).getId() == 'defaultUser.gif'
        self.app.REQUEST['userid'] = 'user_2'
        assert self.pm.getPersonalPortrait(None).getId() == 'user_2'

    def testListMembers(self):
        '''Should return the members list'''
        members = self.pm.listMembers()
        assert len(members) == 1
        assert members[0].getId() == _user_name

    def testListMembersSkipsGroups(self):
        '''Should only return real members, not groups'''
        uf = self.portal.acl_users
        uf.changeOrCreateGroups(new_groups=['Foo', 'Bar'])
        assert len(uf.getUserNames()) == 3
        members = self.pm.listMembers()
        assert len(members) == 1
        assert members[0].getId() == _user_name

    def testCurrentPassword(self):
        '''Password checking should work'''
        assert self.pm.testCurrentPassword('secret')
        assert not self.pm.testCurrentPassword('geheim')

    def testSetPassword(self):
        '''Password should be changed'''
        self.pm.setPassword('geheim')
        assert self.pm.testCurrentPassword('geheim')

    def testSetPasswordIfAnonymous(self):
        '''Anonymous should not be able to change password'''
        self.logout()
        try:
            self.pm.setPassword('geheim')
        except:
            # Bl**dy string exceptions
            import sys; e, v, tb = sys.exc_info(); del tb
            if str(e) == 'Bad Request' and str(v) == 'Not logged in.': 
                pass    # Test passed
            else:
                raise


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestMembershipTool))
        return suite

