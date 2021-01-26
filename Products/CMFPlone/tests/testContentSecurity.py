from AccessControl import Unauthorized
from Acquisition import aq_base
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zExceptions.unauthorized import Unauthorized as zUnauthorized
from zope.component import getMultiAdapter


class TestContentSecurity(PloneTestCase):

    def afterSetUp(self):
        self.request = self.layer["request"]
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('user2', 'secret', ['Member'], [])
        #_ender_'s member who's not a Member usecase
        self.portal.acl_users._doAddUser('user3', 'secret', [], [])
        self.membership = self.portal.portal_membership
        self.workflow = self.portal.portal_workflow
        self.createMemberarea('user1')
        self.createMemberarea('user2')

    def setup_authenticator(self):
        from plone.protect.authenticator import createToken

        self.request.form["_authenticator"] = createToken()

    def get_content_status_modify_view(self, obj):
        self.setup_authenticator()
        view = getMultiAdapter((obj, self.request), name="content_status_modify")
        return view

    def testCreateMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')
        self.assertTrue(hasattr(aq_base(folder), 'new'))

    def testCreateOtherMemberContentFails(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user2')
        with self.assertRaises(zUnauthorized):
            folder.invokeFactory('Document', 'new')

    def testCreateRootContentFails(self):
        self.login('user1')
        with self.assertRaises(Unauthorized):
            self.portal.invokeFactory('Document', 'new')

    def testDeleteMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')
        folder.manage_delObjects(['new'])
        self.assertFalse(hasattr(aq_base(folder), 'new'))

    def testDeleteOtherMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')

        self.login('user2')
        folder = self.membership.getHomeFolder('user1')
        with self.assertRaises(zUnauthorized):
            folder.manage_delObjects(['new'])

    def testCreateWithLocalRole(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Owner',))
        self.login('user2')
        # This will raise Unauthorized if the role is not set
        folder.invokeFactory('Document', id='new')

    def testCreateFailsWithLocalRoleBlocked(self):
        # Ensure that local role blocking works for blocking content creation
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Owner',))

        sharingView = self.folder.unrestrictedTraverse('@@sharing')
        sharingView.update_role_settings([{'id': 'user2',
                                           'type': 'user',
                                           'roles': ['Owner']}])

        folder.invokeFactory('Folder', id='subfolder')
        # Turn off local role acquisition
        folder.subfolder.unrestrictedTraverse('@@sharing') \
            .update_inherit(False)

        self.login('user2')
        # This should now raise ValueError
        with self.assertRaises(zUnauthorized):
            folder.subfolder.invokeFactory('Document', 'new')

    def testCreateSucceedsWithLocalRoleBlockedInParentButAssingedInSubFolder(self):
        # Make sure that blocking a acquisition in a folder does not interfere
        # with assigning a role in subfolders
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Owner',))
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        # Turn off local role acquisition
        subfolder.unrestrictedTraverse('@@sharing').update_inherit(False)
        subfolder.invokeFactory('Folder', id='subsubfolder')
        subfolder.subsubfolder.manage_addLocalRoles('user2', ('Owner',))
        self.login('user2')
        # This should not raise Unauthorized
        subfolder.subsubfolder.invokeFactory('Document', id='new')

    def testViewAllowedOnContentInAcquisitionBlockedFolder(self):
        # Test for http://dev.plone.org/plone/ticket/4055 which seems to be
        # invalid
        self.login('user1')
        self.setupAuthenticator()
        folder = self.membership.getHomeFolder('user1')
        self.setRequestMethod('POST')
        folder.manage_addLocalRoles('user2', ('Owner',))
        self.setRequestMethod('GET')
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        subfolder.unrestrictedTraverse('@@sharing').update_inherit(False)
        # Turn off local role acquisition
        subfolder.invokeFactory('Document', id='new')
        view = self.get_content_status_modify_view(subfolder.new)
        view(workflow_action='publish')
        subfolder.new.manage_addLocalRoles('user2', ('Member',))
        self.login('user2')
        # This should not raise Unauthorized
        subfolder.new.view()

    def testViewAllowedOnContentInPrivateFolder(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        view = self.get_content_status_modify_view(folder)
        view(workflow_action='private')
        folder.invokeFactory('Document', id='doc1')
        doc = folder.doc1
        view = self.get_content_status_modify_view(doc)
        view(workflow_action='publish')
        doc.manage_addLocalRoles('user2', ('Owner',))
        self.login('user2')
        # This should not raise Unauthorized
        doc.view()
        # Neither should anonymous
        self.logout()
        doc.view()

    def testViewAllowedOnContentInAcquisitionBlockedFolderWithCustomWorkflow(self):
        # Another test for http://dev.plone.org/plone/ticket/4055
        # using a paired down version of the custom workflow described therein
        # 'Access contents information' must be enabled for Authenticated/
        # Anonymous on folders for even simple actions to evaluate properly.

        # Create more private workflow starting with folder_workflow
        wf = self.portal.portal_workflow.folder_workflow
        visible = wf.states.visible
        visible.setPermission('View', 0, ('Manager', 'Owner'))
        visible.setPermission('Modify portal content', 0, ('Manager', 'Owner'))
        # Then plone workflow
        p_wf = self.portal.portal_workflow.plone_workflow
        published = p_wf.states.published
        published.setPermission('View', 0, ('Manager', 'Member', 'Owner'))
        published.setPermission('Access contents information', 0,
                                ('Manager', 'Member', 'Owner'))
        published.setPermission('Modify portal content', 0,
                                ('Manager', 'Member', 'Owner'))
        self.portal.portal_workflow.updateRoleMappings()

        self.login('user1')
        self.setupAuthenticator()
        self.setRequestMethod('POST')
        folder = self.membership.getHomeFolder('user1')
        self.setRequestMethod('GET')
        folder.manage_addLocalRoles('user2', ('Member',))
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        subfolder.unrestrictedTraverse('@@sharing').update_inherit(False)
        subfolder.invokeFactory('Document', id='new')
        view = self.get_content_status_modify_view(subfolder.new)
        view(workflow_action='publish')
        subfolder.new.manage_addLocalRoles('user3', ('Member',))
        self.login('user3')
        # This shouldn't either, but strangely it never does even if the script
        # below, which is called in here, does.  What is wrong here?
        try:
            subfolder.new.view()
        except Unauthorized:
            self.fail("Could not access base_view on 'new'")
        # This should not raise Unauthorized
