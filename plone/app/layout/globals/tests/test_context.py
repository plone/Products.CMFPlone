# -*- coding: utf-8 -*-
from plone.app.layout.globals.tests.base import GlobalsTestCase
from plone.app.testing import TEST_USER_ID
from plone.locking.interfaces import ILockable
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.utils import _createObjectByType
from zope.interface import directlyProvides


class TestContextStateView(GlobalsTestCase):
    """Ensure that the basic redirector setup is successful.
    """

    def afterSetUp(self):
        self.fview = self.folder.restrictedTraverse('@@plone_context_state')

        self.folder.invokeFactory('Document', 'd1')
        self.folder.setDefaultPage('d1')
        self.dview = self.folder.d1.restrictedTraverse('@@plone_context_state')

        self.folder.invokeFactory('Folder', 'f1')
        directlyProvides(self.folder.f1, INonStructuralFolder)
        self.sview = self.folder.f1.restrictedTraverse('@@plone_context_state')

        self.pview = self.portal.restrictedTraverse('@@plone_context_state')

    def test_current_page_url(self):
        url = self.folder.absolute_url() + '/some_view'
        self.app.REQUEST['ACTUAL_URL'] = url
        self.app.REQUEST['QUERY_STRING'] = 'foo=bar'
        self.assertEqual(self.fview.current_page_url(), url + '?foo=bar')

    def test_current_base_url(self):
        url = self.folder.absolute_url() + '/some_view'
        self.app.REQUEST['ACTUAL_URL'] = url
        self.app.REQUEST['QUERY_STRING'] = 'foo=bar'
        self.assertEqual(self.fview.current_base_url(), url)

    def test_canonical_object(self):
        self.assertEqual(self.fview.canonical_object(), self.folder)
        self.assertEqual(self.dview.canonical_object(), self.folder)

    def test_canonical_object_url(self):
        self.assertEqual(
            self.fview.canonical_object_url(), self.folder.absolute_url())
        self.assertEqual(
            self.dview.canonical_object_url(), self.folder.absolute_url())

    def test_view_url(self):
        self.assertEqual(
            self.fview.view_url(),
            self.folder.absolute_url()
        )
        self.assertEqual(
            self.dview.view_url(),
            self.folder.d1.absolute_url()
        )
        self.folder.invokeFactory('File', 'file1')
        self.fileview = self.folder.file1.restrictedTraverse(
            '@@plone_context_state')
        self.assertEqual(
            self.fileview.view_url(),
            self.folder.file1.absolute_url() + '/view'
        )

    def test_view_template_id(self):
        self.folder.setLayout('foo_view')
        self.assertEqual(self.fview.view_template_id(), 'foo_view')

    def test_view_template_id_nonbrowserdefault(self):
        # The view template id is taken from the FTI for non-browserdefault
        # (non ATContentTypes) content
        tf = _createObjectByType('TempFolder', self.folder, 'tf')
        tfview = tf.restrictedTraverse('@@plone_context_state')
        self.assertEqual(tfview.view_template_id(), 'index_html')

    def test_view_template_id_nonbrowserdefault_nonempty(self):
        # The view template id is taken from the FTI for non-browserdefault
        # (non ATContentTypes) content. In this case the default view action
        # includes an actual template name

        # Set the expression to include a view name.
        fti = self.portal.portal_types.TempFolder
        view_action = fti.getActionObject('object/view')
        view_expression = view_action.getActionExpression()
        view_action.setActionExpression('foobar')

        tf = _createObjectByType('TempFolder', self.folder, 'tf')
        tf.manage_addLocalRoles(TEST_USER_ID, ('Manager', ))
        tfview = tf.restrictedTraverse('@@plone_context_state')
        self.assertEqual(tfview.view_template_id(), 'foobar')

        # Reset the FTI action expression
        view_action.setActionExpression(view_expression)

    def test_view_template_id_nonbrowserdefault_restricted(self):
        # The view template id is taken from the FTI for non-browserdefault
        # (non ATContentTypes) content. If the view action is protected by
        # a non-default permission, this should still work if the current
        # user has the right permission, locally.

        # Set access to something the default user does not have, normally
        fti = self.portal.portal_types.TempFolder
        view_action = fti.getActionObject('object/view')
        view_perms = view_action.getPermissions()
        view_action.edit(permissions=(u'Modify Portal Content', ))

        tf = _createObjectByType('TempFolder', self.folder, 'tf')
        tf.manage_addLocalRoles(TEST_USER_ID, ('Manager', ))
        tfview = tf.restrictedTraverse('@@plone_context_state')
        self.assertEqual(tfview.view_template_id(), 'index_html')

        # Reset the FTI permissions
        view_action.edit(permissions=view_perms)

    def test_is_view_template_default_page(self):
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url()
        # Whether you're viewing the folder or its default page ...
        self.assertEqual(self.fview.is_view_template(), True)
        self.assertEqual(self.dview.is_view_template(), True)

    def test_is_view_template_trailing_slash(self):
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url() + '/'
        self.assertEqual(self.fview.is_view_template(), True)
        self.assertEqual(self.dview.is_view_template(), True)

    def test_is_view_template_template(self):
        self.folder.setLayout('foo_view')
        self.app.REQUEST[
            'ACTUAL_URL'] = self.folder.absolute_url() + '/foo_view'
        self.assertEqual(self.fview.is_view_template(), True)
        self.assertEqual(self.dview.is_view_template(), False)

    def test_is_view_template_template_z3view(self):
        self.folder.setLayout('foo_view')
        self.app.REQUEST[
            'ACTUAL_URL'] = self.folder.absolute_url() + '/@@foo_view'
        self.assertEqual(self.fview.is_view_template(), True)
        self.assertEqual(self.dview.is_view_template(), False)

    def test_is_view_template_view(self):
        self.folder.setLayout('foo_view')
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url() + '/view'
        self.assertEqual(self.fview.is_view_template(), True)
        self.assertEqual(self.dview.is_view_template(), False)

    def test_is_view_template_other(self):
        self.folder.setLayout('foo_view')
        self.app.REQUEST[
            'ACTUAL_URL'] = self.folder.absolute_url() + '/bar_view'
        self.assertEqual(self.fview.is_view_template(), False)
        self.assertEqual(self.dview.is_view_template(), False)

    def test_is_view_template_edit(self):
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url() + '/edit'
        self.assertEqual(self.fview.is_view_template(), False)
        self.assertEqual(self.dview.is_view_template(), False)

    def test_is_view_template_alias(self):
        browserDefault = IBrowserDefault(self.folder, None)
        fti = browserDefault.getTypeInfo()
        aliases = fti.getMethodAliases()
        aliases['foo_alias'] = '(Default)'
        fti.setMethodAliases(aliases)
        self.app.REQUEST[
            'ACTUAL_URL'] = self.folder.absolute_url() + '/foo_alias'
        self.assertEqual(self.fview.is_view_template(), True)
        self.assertEqual(self.dview.is_view_template(), False)

    def test_object_url(self):
        self.assertEqual(self.fview.object_url(), self.folder.absolute_url())
        self.assertEqual(
            self.dview.object_url(), self.folder.d1.absolute_url())

    def test_object_title(self):
        self.folder.d1.setTitle('My title')
        self.assertEqual(self.dview.object_title(), 'My title')

    def test_workflow_state(self):
        wfstate = self.portal.portal_workflow.getInfoFor(
            self.folder.d1, 'review_state')
        self.assertEqual(self.dview.workflow_state(), wfstate)

    def test_parent(self):
        self.assertEqual(self.dview.parent(), self.folder)
        self.assertEqual(self.sview.parent(), self.folder)

    def test_folder(self):
        self.assertEqual(self.fview.folder(), self.folder)
        self.assertEqual(self.dview.folder(), self.folder)
        self.assertEqual(self.sview.folder(), self.folder)

    def test_is_folderish(self):
        self.assertEqual(self.fview.is_folderish(), True)
        self.assertEqual(self.dview.is_folderish(), False)
        self.assertEqual(self.sview.is_folderish(), True)

    def test_is_structural_folder(self):
        self.assertEqual(self.fview.is_structural_folder(), True)
        self.assertEqual(self.dview.is_structural_folder(), False)
        self.assertEqual(self.sview.is_structural_folder(), False)

    def test_is_default_page(self):
        self.assertEqual(self.fview.is_default_page(), False)
        self.assertEqual(self.dview.is_default_page(), True)
        self.assertEqual(self.sview.is_default_page(), False)

    def test_is_portal_root(self):
        self.assertEqual(self.fview.is_portal_root(), False)
        self.assertEqual(self.dview.is_portal_root(), False)
        self.assertEqual(self.sview.is_portal_root(), False)
        self.assertEqual(self.pview.is_portal_root(), True)

    def test_is_editable(self):
        self.assertEqual(self.dview.is_editable(), True)
        self.logout()
        del self.app.REQUEST.__annotations__
        self.assertEqual(self.dview.is_editable(), False)

    def test_is_locked(self):
        self.assertEqual(self.dview.is_locked(), False)
        ILockable(self.folder.d1).lock()
        self.logout()
        # The object is not "locked" if it was locked by the
        # current user
        del self.app.REQUEST.__annotations__
        self.assertEqual(self.dview.is_locked(), True)

    def test_actions(self):
        actions = self.fview.actions('user')
        self.assertTrue(actions[0]['category'] == 'user')
