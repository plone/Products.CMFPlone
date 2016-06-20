from Products.PloneTestCase import PloneTestCase as ptc

from zope.component import queryUtility
from StringIO import StringIO

from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import AuthenticatorView


class AuthenticatorTestCase(ptc.FunctionalTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def test_KeyManager(self):
        self.assertTrue(queryUtility(IKeyManager), 'key manager not found')

    def checkAuthenticator(self, path, query='', status=200):
        credentials = '%s:%s' % (ptc.default_user, ptc.default_password)
        path = '/' + self.portal.absolute_url(relative=True) + path
        data = StringIO(query)
        # without authenticator...
        response = self.publish(path=path, basic=credentials, env={},
                                request_method='POST', stdin=data)
        self.assertEqual(response.getStatus(), 403)
        # with authenticator...
        tag = AuthenticatorView('context', 'request').authenticator()
        token = tag.split('"')[5]
        data = StringIO(query + '&_authenticator=%s' % token)
        response = self.publish(path=path, basic=credentials, env={},
                                request_method='POST', stdin=data)
        self.assertEqual(response.getStatus(), status)

    def test_PloneTool_changeOwnershipOf(self):
        self.assertNotEqual(self.portal.getOwner().getUserName(),
                            ptc.default_user)
        self.checkAuthenticator('/change_ownership',
            'userid=%s' % ptc.default_user, status=302)
        self.assertEqual(self.portal.getOwner().getUserName(),
                         ptc.default_user)

    def test_PloneTool_deleteObjectsByPaths(self):
        self.assertTrue(self.portal.get('news', None))
        news = self.portal.get('news', None)
        self.checkAuthenticator('/plone_utils/deleteObjectsByPaths',
            'paths:list='+news.absolute_url_path())
        self.assertFalse(self.portal.get('news', None))

    def test_PloneTool_transitionObjectsByPaths(self):
        infoFor = self.portal.portal_workflow.getInfoFor
        frontpage = self.portal['front-page']
        self.assertEqual(infoFor(frontpage, 'review_state'), 'visible')
        self.checkAuthenticator(
            '/plone_utils/transitionObjectsByPaths',
            'workflow_action=publish&paths:list=front-page', status=302)
        self.assertEqual(infoFor(frontpage, 'review_state'), 'published')

    def test_PloneTool_renameObjectsByPaths(self):
        self.assertFalse(self.portal.get('foo', None))
        self.checkAuthenticator(
            '/plone_utils/renameObjectsByPaths',
            'paths:list=events&new_ids:list=foo&new_titles:list=Foo')
        self.assertTrue(self.portal.get('foo', None))

    def test_RegistrationTool_addMember(self):
        # self.checkAuthenticator(
        #    '/portal_registration/addMember',
        #    'id=john&password=y0d4Wg')
        # instead of authenticator, with latest patch, addMember should not
        # be published
        path = '/portal_registration/addMember'
        path = '/' + self.portal.absolute_url(relative=True) + path
        query = 'id=john&password=y0d4Wg'
        data = StringIO(query)
        response = self.publish(path=path, env={},
                                request_method='POST', stdin=data)
        self.assertEqual(response.getStatus(), 404)

    def test_RegistrationTool_editMember(self):
        self.checkAuthenticator(
            '/portal_registration/editMember',
            'member_id=%s&password=y0d4Wg&properties.foo:record='
                    % ptc.default_user)

    def test_MembershipTool_setPassword(self):
        self.checkAuthenticator(
            '/portal_membership/setPassword',
            'password=y0d4Wg')

    def test_MembershipTool_deleteMemberArea(self):
        self.checkAuthenticator(
            '/portal_membership/deleteMemberArea',
            'member_id=%s' % ptc.default_user)

    def test_MembershipTool_deleteMembers(self):
        self.checkAuthenticator(
            '/portal_membership/deleteMembers',
            'member_ids:list=%s' % ptc.default_user)

    def test_userFolderAddUser(self):
        self.checkAuthenticator(
            '/acl_users/userFolderAddUser',
            'login=foo&password=bar&domains=&roles:list=Manager')

    def test_userFolderEditUser(self):
        self.checkAuthenticator(
            '/acl_users/userFolderEditUser',
            'principal_id=%s&password=bar&domains=&roles:list=Manager'
                % ptc.default_user)

    def test_userFolderDelUsers(self):
        self.checkAuthenticator(
            '/acl_users/userFolderDelUsers',
            'names:list=%s' % ptc.default_user)
