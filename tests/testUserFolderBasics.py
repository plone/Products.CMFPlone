#
# Generic User Folder tests. Every User Folder implementation 
# must pass these.
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

_user_name = ZopeTestCase._user_name
_standard_permissions = ZopeTestCase._standard_permissions
_user_role = 'Member'
_pm = 'ThePublishedMethod'

from AccessControl import Unauthorized


class TestBase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.logout()
        self.uf = self.portal.acl_users
    
    def _setupPublishedMethod(self):
        self.folder.addDTMLMethod(_pm, file='some content')
        pm = self.folder[_pm]
        for p in _standard_permissions:
            pm.manage_permission(p, [_user_role], acquire=0)

    def _setupPublishedRequest(self):
        request = self.app.REQUEST
        request.set('PUBLISHED', self.folder[_pm])
        request.set('PARENTS', [self.folder, self.app])
        folder_path = self.folder.absolute_url(1).split('/')
        request.steps = folder_path + [_pm]

    def _basicAuth(self, name):
        import base64
        return 'Basic %s' % base64.encodestring('%s:%s' %(name, 'secret'))

    def _call__roles__(self, object):
        # From BaseRequest.traverse()
        roles = ()
        object = getattr(object, 'aq_base', object)
        if hasattr(object, '__call__') and hasattr(object.__call__, '__roles__'):
            roles = object.__call__.__roles__
        return roles


class TestUserFolderSecurity(TestBase):
    '''Test UF is working'''

    def testGetUser(self):
        assert self.uf.getUser(_user_name) is not None

    def testGetUsers(self):
        users = self.uf.getUsers()
        assert users != []
        assert users[0].getUserName() == _user_name

    def testGetUserNames(self):
        names = self.uf.getUserNames()
        assert names != []
        assert names[0] == _user_name

    def testIdentify(self):
        auth = self._basicAuth(_user_name)
        name, password = self.uf.identify(auth)
        assert name is not None
        assert name == _user_name
        assert password is not None
    
    def testGetRoles(self):
        user = self.uf.getUser(_user_name)
        assert _user_role in user.getRoles()
    
    def testGetRolesInContext(self):
        user = self.uf.getUser(_user_name)
        self.folder.manage_addLocalRoles(_user_name, ['Owner'])
        roles = user.getRolesInContext(self.folder)
        assert _user_role in roles
        assert 'Owner' in roles
    
    def testHasRole(self):
        user = self.uf.getUser(_user_name)
        assert user.has_role(_user_role, self.folder)
    
    def testHasLocalRole(self):
        user = self.uf.getUser(_user_name)
        self.folder.manage_addLocalRoles(_user_name, ['Owner'])
        assert user.has_role('Owner', self.folder)
    
    def testHasPermission(self):
        user = self.uf.getUser(_user_name)
        self.folder.manage_role(_user_role, _standard_permissions+['Add Folders'])
        self.login()   # !!! Fixed in Zope 2.6.2
        assert user.has_permission('Add Folders', self.folder)
    
    def testHasLocalPermission(self):
        user = self.uf.getUser(_user_name)
        self.folder.manage_role('Owner', ['Add Folders'])
        self.folder.manage_addLocalRoles(_user_name, ['Owner'])
        self.login()   # !!! Fixed in Zope 2.6.2
        assert user.has_permission('Add Folders', self.folder)
    
    def testAuthenticate(self):
        user = self.uf.getUser(_user_name) 
        assert user.authenticate('secret', self.app.REQUEST)

    
class TestUserFolderAccess(TestBase):
    '''Test UF is protecting access'''

    def afterSetUp(self):
        TestBase.afterSetUp(self)
        self._setupPublishedMethod()
            
    def testAllowAccess(self):
        self.login()
        try:
            self.folder.restrictedTraverse(_pm)
        except Unauthorized:
            self.fail('Unauthorized')
    
    def testDenyAccess(self):                                                                                       
        self.assertRaises(Unauthorized, self.folder.restrictedTraverse, _pm)


class TestUserFolderValidate(TestBase):
    '''Test UF is authorizing us'''

    def afterSetUp(self):
        TestBase.afterSetUp(self)
        self._setupPublishedMethod()
        self._setupPublishedRequest()

    def testAuthorize(self):
        # Validate should log us in
        request = self.app.REQUEST
        auth = self._basicAuth(_user_name)
        user = self.uf.validate(request, auth, [_user_role])
        assert user is not None
        assert user.getUserName() == _user_name

    def testNotAuthorize(self):
        # Validate should fail without auth
        request = self.app.REQUEST
        auth = ''
        assert self.uf.validate(request, auth, [_user_role]) is None

    def testNotAuthorize2(self):
        # Validate should fail without roles
        request = self.app.REQUEST
        auth = self._basicAuth(_user_name)
        assert self.uf.validate(request, auth) is None

    def testNotAuthorize3(self):
        # Validate should fail with wrong roles
        request = self.app.REQUEST
        auth = self._basicAuth(_user_name)
        assert self.uf.validate(request, auth, ['Manager']) is None

    def testAuthorize2(self):
        # Validate should allow us to call dm
        request = self.app.REQUEST                                                                                  
        auth = self._basicAuth(_user_name)
        roles = self._call__roles__(self.folder[_pm])
        user = self.uf.validate(request, auth, roles)
        assert user is not None
        assert user.getUserName() == _user_name

    def testNotAuthorize4(self):
        # Validate should deny us to call dm
        request = self.app.REQUEST
        auth = self._basicAuth(_user_name)
        pm = self.folder[_pm]
        for p in _standard_permissions:
            pm.manage_permission(p, [], acquire=0)
        roles = self._call__roles__(pm)
        assert self.uf.validate(request, auth, roles) is None


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestUserFolderSecurity))
        suite.addTest(unittest.makeSuite(TestUserFolderAccess))
        suite.addTest(unittest.makeSuite(TestUserFolderValidate))
        return suite

