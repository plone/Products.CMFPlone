#
# Generic User Folder tests. Every User Folder implementation
# must pass these.
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

default_user = ZopeTestCase.user_name
user_perms   = ZopeTestCase.standard_permissions
user_role    = 'Member'

_pm = 'ThePublishedMethod'

from AccessControl import Unauthorized


class TestBase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.logout()
        self.uf = self.portal.acl_users

    def _setupPublishedMethod(self):
        self.folder.addDTMLMethod(_pm, file='some content')
        pm = self.folder[_pm]
        for p in user_perms:
            pm.manage_permission(p, [user_role], acquire=0)

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
        self.failIf(self.uf.getUser(default_user) is None)

    def testGetUsers(self):
        users = self.uf.getUsers()
        self.failUnless(users)
        self.assertEqual(users[0].getUserName(), default_user)

    def testGetUserNames(self):
        names = self.uf.getUserNames()
        self.failUnless(names)
        self.assertEqual(names[0], default_user)

    def testIdentify(self):
        auth = self._basicAuth(default_user)
        name, password = self.uf.identify(auth)
        self.failIf(name is None)
        self.assertEqual(name, default_user)
        self.failIf(password is None)

    def testGetRoles(self):
        user = self.uf.getUser(default_user)
        self.failUnless(user_role in user.getRoles())

    def testGetRolesInContext(self):
        user = self.uf.getUser(default_user)
        self.folder.manage_addLocalRoles(default_user, ['Owner'])
        roles = user.getRolesInContext(self.folder)
        self.failUnless(user_role in roles)
        self.failUnless('Owner' in roles)

    def testHasRole(self):
        user = self.uf.getUser(default_user)
        self.failUnless(user.has_role(user_role, self.folder))

    def testHasLocalRole(self):
        user = self.uf.getUser(default_user)
        self.folder.manage_addLocalRoles(default_user, ['Owner'])
        self.failUnless(user.has_role('Owner', self.folder))

    def testHasPermission(self):
        user = self.uf.getUser(default_user)
        self.folder.manage_role(user_role, user_perms+['Add Folders'])
        self.login()   # !!! Fixed in Zope 2.6.2
        self.failUnless(user.has_permission('Add Folders', self.folder))

    def testHasLocalPermission(self):
        user = self.uf.getUser(default_user)
        self.folder.manage_role('Owner', ['Add Folders'])
        self.folder.manage_addLocalRoles(default_user, ['Owner'])
        self.login()   # !!! Fixed in Zope 2.6.2
        self.failUnless(user.has_permission('Add Folders', self.folder))

    def testAuthenticate(self):
        user = self.uf.getUser(default_user)
        self.failUnless(user.authenticate('secret', self.app.REQUEST))


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
        auth = self._basicAuth(default_user)
        user = self.uf.validate(request, auth, [user_role])
        self.failIf(user is None)
        self.assertEqual(user.getUserName(), default_user)

    def testNotAuthorize(self):
        # Validate should fail without auth
        request = self.app.REQUEST
        auth = ''
        self.assertEqual(self.uf.validate(request, auth, [user_role]), None)

    def testNotAuthorize2(self):
        # Validate should fail without roles
        request = self.app.REQUEST
        auth = self._basicAuth(default_user)
        self.assertEqual(self.uf.validate(request, auth), None)

    def testNotAuthorize3(self):
        # Validate should fail with wrong roles
        request = self.app.REQUEST
        auth = self._basicAuth(default_user)
        self.assertEqual(self.uf.validate(request, auth, ['Manager']), None)

    def testAuthorize2(self):
        # Validate should allow us to call dm
        request = self.app.REQUEST
        auth = self._basicAuth(default_user)
        roles = self._call__roles__(self.folder[_pm])
        user = self.uf.validate(request, auth, roles)
        self.failIf(user is None)
        self.assertEqual(user.getUserName(), default_user)

    def testNotAuthorize4(self):
        # Validate should deny us to call dm
        request = self.app.REQUEST
        auth = self._basicAuth(default_user)
        pm = self.folder[_pm]
        for p in user_perms:
            pm.manage_permission(p, [], acquire=0)
        roles = self._call__roles__(pm)
        self.assertEqual(self.uf.validate(request, auth, roles), None)


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
