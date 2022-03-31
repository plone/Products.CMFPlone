from Acquisition import Explicit
from OFS.SimpleItem import Item
from plone.app.testing import login
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionInfo
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_INTEGRATION_TESTING
from traceback import format_exception
from zope.i18nmessageid.message import Message

import unittest


class ExplicitItem(Item, Explicit):
    '''Item without implicit acquisition'''
    id = 'dummy'
    meta_type = 'Dummy Item'


class TestActionsTool(unittest.TestCase):

    layer = PRODUCTS_CMFPLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.actions = self.portal.portal_actions
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.invokeFactory('Folder', 'f1')
        self.folder = self.portal['f1']

    def fail_tb(self, msg):
        """ special fail for capturing errors """
        import sys
        e, v, tb = sys.exc_info()
        tb = ''.join(format_exception(e, v, tb))
        self.fail(f"{msg}\n{tb}\n")

    def testAddAction(self):
        # addAction should work even though PloneTestCase patches _cloneActions
        action_infos = self.actions.listActions()
        length = len(action_infos)
        self.actions.addAction(id='foo',
                               name='foo_name',
                               action='foo_action',
                               condition='foo_condition',
                               permission='foo_permission',
                               category='foo_category',
                               visible=1)
        action_infos = self.actions.listActions()
        self.assertEqual(len(action_infos), length + 1)
        foo_action = self.actions.getActionObject('foo_category/foo')
        self.assertEqual(foo_action.id, 'foo')
        self.assertEqual(foo_action.title, 'foo_name')
        self.assertEqual(foo_action.permissions, ('foo_permission',))
        self.assertEqual(foo_action.category, 'foo_category')

    def testPortalTypesIsActionProvider(self):
        self.assertTrue('portal_types' in self.actions.listActionProviders())

    def testMissingActionProvider(self):
        self.portal._delObject('portal_types')
        try:
            self.actions.listFilteredActionsFor(self.portal)
        except:
            self.fail_tb('Should not bomb out if a provider is missing')

    def testBrokenActionProvider(self):
        self.portal.portal_types = self.portal.portal_catalog
        try:
            self.actions.listFilteredActionsFor(self.portal)
        except:
            self.fail_tb('Should not bomb out if a provider is broken')

    def testMissingListActions(self):
        self.portal.portal_types = ExplicitItem()
        try:
            self.actions.listFilteredActionsFor(self.portal)
        except:
            self.fail_tb('Should not bomb out if a provider is broken')

    def testDocumentActionsPermissionBug(self):
        # Test to ensure that permissions for items categorized as
        # 'document_actions' have their permissions evaluated in the context
        # of the content object.
        self.actions.addAction(id='foo',
                               name='foo_name',
                               action='foo_action',
                               condition='',
                               permission='View',
                               category='document_actions',
                               visible=1)
        actions = self.actions.listFilteredActionsFor(self.folder)
        match = [a for a in actions['document_actions'] if a['id'] == 'foo']
        self.assertTrue(match)
        login(self.portal, 'user1')
        actions = self.actions.listFilteredActionsFor(self.folder)
        match = [a for a in actions.get('document_actions', [])
                 if a['id'] == 'foo']
        self.assertFalse(match)

    def testActionNamespace(self):
        self.actions.addAction(
            id='foo',
            name='foo_name',
            action='string:${globals_view/isStructuralFolder}',
            condition='',
            permission='View',
            category='folder',
            visible=1)

        actions = self.actions.listFilteredActionsFor(self.folder)
        actions['folder'][0]['url']

    def testAllActionsAreRenderedAsMessages(self):
        actions = self.actions.listActions()
        for action in actions:
            info = ActionInfo(action, self.portal)
            self.assertTrue(isinstance(info['title'], Message))
            self.assertTrue(isinstance(info['description'], Message))

    def testListActionsSkipsItemsWithOldInterface(self):
        # Ticket #10791
        me = Action("not_action_category")
        self.actions['not_a_category'] = me
        try:
            self.actions.listActions()
        except:
            self.fail_tb('Should not fail if item exists w/o IActionCategory '
                         'interface')
