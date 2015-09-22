from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing.bbb import PloneTestCase
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import AuthenticatorView
from StringIO import StringIO
from zope.component import queryUtility


class AuthenticatorTestCase(PloneTestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def test_KeyManager(self):
        self.assertTrue(queryUtility(IKeyManager), 'key manager not found')

    def checkAuthenticator(self, path, query='', status=200):
        credentials = '%s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD)
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

    def test_PloneTool_deleteObjectsByPaths(self):
        self.assertTrue(self.portal.get('news', None))
        self.checkAuthenticator(
            '/plone_utils/deleteObjectsByPaths',
            'paths:list=news')
        self.assertFalse(self.portal.get('news', None))

    def test_PloneTool_transitionObjectsByPaths(self):
        infoFor = self.portal.portal_workflow.getInfoFor
        frontpage = self.portal['front-page']
        self.assertEqual(infoFor(frontpage, 'review_state'), 'published')
        self.checkAuthenticator(
            '/plone_utils/transitionObjectsByPaths',
            'workflow_action=retract&paths:list=front-page', status=302)
        self.assertEqual(infoFor(frontpage, 'review_state'), 'visible')

    def test_PloneTool_renameObjectsByPaths(self):
        self.assertFalse(self.portal.get('foo', None))
        self.checkAuthenticator(
            '/plone_utils/renameObjectsByPaths',
            'paths:list=events&new_ids:list=foo&new_titles:list=Foo')
        self.assertTrue(self.portal.get('foo', None))

    def test_RegistrationTool_editMember(self):
        self.checkAuthenticator(
            '/portal_registration/editMember',
            'member_id=%s&password=y0d4Wg&properties.foo:record=' % (
                TEST_USER_ID))

    def test_MembershipTool_setPassword(self):
        self.checkAuthenticator(
            '/portal_membership/setPassword',
            'password=y0d4Wg')

    def test_MembershipTool_deleteMemberArea(self):
        self.checkAuthenticator(
            '/portal_membership/deleteMemberArea',
            'member_id=%s' % TEST_USER_ID)

    def test_MembershipTool_deleteMembers(self):
        self.checkAuthenticator(
            '/portal_membership/deleteMembers',
            'member_ids:list=%s' % TEST_USER_ID)

    def test_userFolderAddUser(self):
        self.checkAuthenticator(
            '/acl_users/userFolderAddUser',
            'login=foo&password=bar&domains=&roles:list=Manager')

    def test_userFolderEditUser(self):
        self.checkAuthenticator(
            '/acl_users/userFolderEditUser',
            'principal_id=%s&password=bar&domains=&roles:list=Manager'
            % TEST_USER_ID)

    def test_userFolderDelUsers(self):
        self.checkAuthenticator(
            '/acl_users/userFolderDelUsers',
            'names:list=%s' % TEST_USER_ID)
