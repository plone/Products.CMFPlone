#
# Tests content security
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase

from AccessControl import Unauthorized
from Acquisition import aq_base

from zope.app.tests.placelesssetup import setUp, tearDown

class TestContentSecurity(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        setUp()
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('user2', 'secret', ['Member'], [])
        #_ender_'s member who's not a Member usecase
        self.portal.acl_users._doAddUser('user3', 'secret', [], [])
        self.membership = self.portal.portal_membership
        self.workflow= self.portal.portal_workflow
        self.createMemberarea('user1')
        self.createMemberarea('user2')

    def testCreateMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')
        self.failUnless(hasattr(aq_base(folder), 'new'))

    def testCreateOtherMemberContentFails(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user2')
        self.assertRaises(Unauthorized, folder.invokeFactory, 'Document', 'new')

    def testCreateRootContentFails(self):
        self.login('user1')
        self.assertRaises(Unauthorized, self.portal.invokeFactory, 'Document', 'new')

    def testDeleteMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')
        folder.manage_delObjects(['new'])
        self.failIf(hasattr(aq_base(folder), 'new'))

    def testDeleteOtherMemberContent(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')

        self.login('user2')
        folder = self.membership.getHomeFolder('user1')
        self.assertRaises(Unauthorized, folder.manage_delObjects, ['new'])

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
        folder.invokeFactory('Folder', id='subfolder')
        #Turn off local role acquisition
        folder.subfolder.folder_localrole_set(use_acquisition=0)
        self.login('user2')
        # This should now raise Unauthorized
        self.assertRaises(Unauthorized, folder.subfolder.invokeFactory, 'Document', 'new')

    def testCreateSucceedsWithLocalRoleBlockedInParentButAssingedInSubFolder(self):
        # Make sure that blocking a acquisition in a folder does not interfere
        # with assigning a role in subfolders
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Owner',))
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        #Turn off local role acquisition
        subfolder.folder_localrole_set(use_acquisition=0)
        subfolder.invokeFactory('Folder', id='subsubfolder')
        subfolder.subsubfolder.manage_addLocalRoles('user2', ('Owner',))
        self.login('user2')
        # This should not raise Unauthorized
        subfolder.subsubfolder.invokeFactory('Document', id='new')

    def testViewAllowedOnContentInAcquisitionBlockedFolder(self):
        # Test for http://members.plone.org/collector/4055 which seems to be
        # invalid
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Owner',))
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        subfolder.folder_localrole_set(use_acquisition=0)
        #Turn off local role acquisition
        subfolder.invokeFactory('Document', id='new')
        subfolder.new.content_status_modify(workflow_action='publish')
        subfolder.new.manage_addLocalRoles('user2', ('Member',))
        self.login('user2')
        # This should not raise Unauthorized
        subfolder.new.base_view()

    def testViewAllowedOnContentInPrivateFolder(self):
        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.content_status_modify(workflow_action='private')
        folder.invokeFactory('Document', id='doc1')
        doc = folder.doc1
        doc.content_status_modify(workflow_action='publish')
        doc.manage_addLocalRoles('user2', ('Owner',))
        self.login('user2')
        # This should not raise Unauthorized
        doc.base_view()
        # Neither should anonymous
        self.logout()
        doc.base_view()

    def testViewAllowedOnContentInAcquisitionBlockedFolderWithCustomWorkflow(self):
        # Another test for http://members.plone.org/collector/4055
        # using a paired down version of the custom workflow described therein
        # 'Access contents information' must be enabled for Authenticated/
        # Anonymous on folders for even simple actions to evaluate properly.

        # Create more private workflow starting with folder_workflow
        wf = self.portal.portal_workflow.folder_workflow
        visible = wf.states.visible
        visible.setPermission('View',0,('Manager','Owner'))
        visible.setPermission('Modify portal content',0,('Manager','Owner'))
        # Then plone workflow
        p_wf = self.portal.portal_workflow.plone_workflow
        published = p_wf.states.published
        published.setPermission('View',0,('Manager','Member','Owner'))
        published.setPermission('Access contents information',0,('Manager','Member','Owner'))
        published.setPermission('Modify portal content',0,('Manager','Member','Owner'))
        self.portal.portal_workflow.updateRoleMappings()

        self.login('user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Member',))
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        subfolder.folder_localrole_set(use_acquisition=0)
        subfolder.invokeFactory('Document', id='new')
        subfolder.new.content_status_modify(workflow_action='publish')
        subfolder.new.manage_addLocalRoles('user3', ('Member',))
        self.login('user3')
        # This shouldn't either, but strangely it never does even if the script
        # below, which is called in here, does.  What is wrong here?
        try:
            subfolder.new.base_view()
        except Unauthorized:
            self.fail("Could not access base_view on 'new'")
        # This should not raise Unauthorized
        try:
            subfolder.new.getAddableTypesInMenu(('Page','Smart Folder'))
        except Unauthorized:
            self.fail("Could not access getAddableTypesInMenu on 'new'")

    def beforeTearDown(self):
        tearDown()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentSecurity))
    return suite

if __name__ == '__main__':
    framework()
