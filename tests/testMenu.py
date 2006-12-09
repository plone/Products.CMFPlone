#
# CatalogTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.CMFPlone.tests import PloneTestCase

from zope.interface import directlyProvides
from zope.component import getUtility

from zope.app.publisher.interfaces.browser import IBrowserMenu

from Products.CMFCore.Expression import Expression
from Products.CMFPlone.interfaces import IBrowserDefault
from Products.CMFPlone.interfaces import ISelectableConstrainTypes
from Products.CMFPlone.interfaces import INonStructuralFolder

from plone.app.contentmenu.interfaces import IActionsMenu
from plone.app.contentmenu.interfaces import IDisplayMenu
from plone.app.contentmenu.interfaces import IFactoriesMenu
from plone.app.contentmenu.interfaces import IWorkflowMenu

from Products.CMFPlone.utils import _createObjectByType
import dummy

class TestActionsMenu(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.menu = getUtility(IBrowserMenu, name='plone.contentmenu.actions.menu', context=self.folder)
        self.request = self.app.REQUEST

    def testActionsMenuImplementsIBrowserMenu(self):
        self.failUnless(IBrowserMenu.providedBy(self.menu))
    
    def testActionsMenuImplementsIActionsMenu(self):
        self.failUnless(IActionsMenu.providedBy(self.menu))
        
    def testActionsMenuFindsActions(self):
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.failUnless('copy' in [a['extra']['id'] for a in actions])

class TestDisplayMenu(PloneTestCase.PloneTestCase):
    
    def afterSetUp(self):
        self.menu = getUtility(IBrowserMenu, name='plone.contentmenu.display.menu', context=self.folder)
        self.request = self.app.REQUEST

    def testActionsMenuImplementsIBrowserMenu(self):
        self.failUnless(IBrowserMenu.providedBy(self.menu))
    
    def testActionsMenuImplementsIActionsMenu(self):
        self.failUnless(IDisplayMenu.providedBy(self.menu))

    # Template selection

    def testTemplatesIncluded(self):
        actions = self.menu.getMenuItems(self.folder, self.request)
        templates = [a['extra']['id'] for a in actions]
        self.failUnless('folder_listing' in templates)
        
    def testSingleTemplateIncluded(self):
        self.folder.invokeFactory('Document', 'doc1')
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]['extra']['id'], 'document_view')
        
    def testNonBrowserDefaultReturnsNothing(self):
        f = dummy.Folder()
        self.folder._setObject('f1', f)
        actions = self.menu.getMenuItems(self.folder.f1, self.request)
        self.assertEqual(len(actions), 0)
        

    def testDefaultPageIncludesParentOnlyWhenItemHasSingleView(self):
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.setDefaultPage('doc1')
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        self.failUnless('_folderDefaultPageDisplay' in [a['extra']['id'] for a in actions])
        self.failIf('document_view' in [a['extra']['id'] for a in actions])

    def testDefaultPageIncludesParentAndItemViewsWhenItemHasMultipleViews(self):
        fti = self.portal.portal_types['Document']
        documentViews = fti.view_methods + ('base_view',)
        fti.manage_changeProperties(view_methods = documentViews)
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.setDefaultPage('doc1')
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        self.failUnless('_folderDefaultPageDisplay' in [a['extra']['id'] for a in actions])
        self.failUnless('document_view' in [a['extra']['id'] for a in actions])
        self.failUnless('base_view' in [a['extra']['id'] for a in actions])
        
    def testCurrentTemplateSelected(self):
        layout = self.folder.getLayout()
        actions = self.menu.getMenuItems(self.folder, self.request)
        selected = [a['extra']['id'] for a in actions if a['selected']]
        self.assertEqual(selected, ['folder_listing'])
        
    # Default-page selection

    def testFolderCanSetDefaultPage(self):
        self.folder.invokeFactory('Folder', 'f1')
        self.failUnless(self.folder.f1.canSetDefaultPage())
        actions = self.menu.getMenuItems(self.folder.f1, self.request)
        self.failUnless('_contextSetDefaultPage' in [a['extra']['id'] for a in actions])
        
    def testWithCanSetDefaultPageFalse(self):
        self.folder.invokeFactory('Folder', 'f1')
        self.folder.f1.manage_permission('Modify view template', ('Manager',))
        self.failIf(self.folder.f1.canSetDefaultPage())
        actions = self.menu.getMenuItems(self.folder.f1, self.request)
        self.failIf('_contextSetDefaultPage' in [a['extra']['id'] for a in actions])
    
    def testSelectItemNotIncludedInNonStructuralFolder(self):
        self.folder.invokeFactory('Folder', 'f1')
        directlyProvides(self.folder.f1, INonStructuralFolder)
        actions = self.menu.getMenuItems(self.folder.f1, self.request)
        self.failIf('_contextSetDefaultPage' in [a['extra']['id'] for a in actions])
        
    def testDefaultPageSelectedAndOverridesLayout(self):
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.setDefaultPage('doc1')
        actions = self.menu.getMenuItems(self.folder, self.request)
        selected = [a['extra']['id'] for a in actions if a['selected']]
        self.assertEqual(selected, ['_contextDefaultPageDisplay'])
    
    def testDefaultPageCanBeChangedInContext(self):
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.setDefaultPage('doc1')
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.failUnless('_contextChangeDefaultPage' in [a['extra']['id'] for a in actions])
                
    def testDefaultPageCanBeChangedInFolder(self):
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.setDefaultPage('doc1')
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        self.failUnless('_folderChangeDefaultPage' in [a['extra']['id'] for a in actions])
        self.failIf('_contextChangeDefaultPage' in [a['extra']['id'] for a in actions])
        
    # Headers/separators
        
    def testSeparatorsIncludedWhenViewingDefaultPageWithViews(self):
        fti = self.portal.portal_types['Document']
        documentViews = fti.view_methods + ('base_view',)
        fti.manage_changeProperties(view_methods = documentViews)
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.setDefaultPage('doc1')
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        ids = [a['extra']['id'] for a in actions]
        self.failUnless('_folderHeader' in ids)
        self.failUnless('_contextHeader' in ids)

    def testSeparatorsNotIncludedWhenViewingDefaultPageWithoutViews(self):
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.setDefaultPage('doc1')
        self.assertEqual(len(self.folder.doc1.getAvailableLayouts()), 1)
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        ids = [a['extra']['id'] for a in actions]
        self.failIf('_folderHeader' in ids)
        self.failIf('_contextHeader' in ids)

    def testSeparatorsNotDisplayedWhenViewingFolder(self):
        fti = self.portal.portal_types['Document']
        documentViews = fti.view_methods + ('base_view',)
        fti.manage_changeProperties(view_methods = documentViews)
        self.folder.invokeFactory('Document', 'doc1')
        self.folder.setDefaultPage('doc1')
        actions = self.menu.getMenuItems(self.folder, self.request)
        ids = [a['extra']['id'] for a in actions]
        self.failIf('_folderHeader' in ids)
        self.failIf('_contextHeader' in ids)

class TestFactoriesMenu(PloneTestCase.PloneTestCase):
    
    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'doc1')
        self.menu = getUtility(IBrowserMenu, name='plone.contentmenu.factories.menu', context=self.folder)
        self.request = self.app.REQUEST

    def testMenuImplementsIBrowserMenu(self):
        self.failUnless(IBrowserMenu.providedBy(self.menu))
    
    def testMenuImplementsIFactoriesMenu(self):
        self.failUnless(IFactoriesMenu.providedBy(self.menu))
        
    def testMenuIncludesFactories(self):
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.failUnless('Image' in [a['extra']['id'] for a in actions])
        
    def testMenuIncludesFactoriesOnNonFolderishContext(self):
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        img = None
        for a in actions:
            if a['extra']['id'] == 'Image':
                img = a
                break
        self.failIf(img is None)
        action = img['action']
        url = self.folder.absolute_url()
        self.failUnless(action.startswith(url))
        url = self.folder.doc1.absolute_url()
        self.failIf(action.startswith(url))
        
    def testNoAddableTypes(self):
        actions = self.menu.getMenuItems(self.portal, self.request)
        self.assertEqual(len(actions), 0)

    def testConstrainTypes(self):
        constraints = ISelectableConstrainTypes(self.folder)
        constraints.setConstrainTypesMode(1)
        constraints.setLocallyAllowedTypes(('Document',))
        constraints.setImmediatelyAddableTypes(('Document',))
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]['extra']['id'], 'Document')
        self.assertEqual(actions[1]['extra']['id'], '_settings')
        
    def testSettingsIncluded(self):
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.assertEqual(actions[-1]['extra']['id'], '_settings')

    def testSettingsNotIncludedWhereNotSupported(self):
        self.folder.manage_permission('Modify constrain types', ('Manager',))
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.failIf('_settings' in [a['extra']['id'] for a in actions])

    def testMoreIncluded(self):
        constraints = ISelectableConstrainTypes(self.folder)
        constraints.setConstrainTypesMode(1)
        constraints.setLocallyAllowedTypes(('Document', 'Image',))
        constraints.setImmediatelyAddableTypes(('Document',))
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.failIf('Image' in [a['extra']['id'] for a in actions])
        self.failUnless('Document' in [a['extra']['id'] for a in actions])
        self.failUnless('_more' in [a['extra']['id'] for a in actions])
        self.failUnless('_settings' in [a['extra']['id'] for a in actions])

    def testMoreNotIncludedWhenNotNecessary(self):
        constraints = ISelectableConstrainTypes(self.folder)
        constraints.setConstrainTypesMode(1)
        constraints.setLocallyAllowedTypes(('Document',))
        constraints.setImmediatelyAddableTypes(('Document',))
        actions = self.menu.getMenuItems(self.folder, self.request)
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0]['extra']['id'], 'Document')
        self.assertEqual(actions[1]['extra']['id'], '_settings')
        
    def testNonStructualFolderShowsParent(self):
        self.folder.invokeFactory('Folder', 'folder1')
        directlyProvides(self.folder.folder1, INonStructuralFolder)
        constraints = ISelectableConstrainTypes(self.folder.folder1)
        constraints.setConstrainTypesMode(1)
        constraints.setLocallyAllowedTypes(('Document',))
        constraints.setImmediatelyAddableTypes(('Document',))
        actions = self.menu.getMenuItems(self.folder.folder1, self.request)
        self.failUnless('Event' in actions[0]['extra']['id'])
        
class TestWorkflowMenu(PloneTestCase.PloneTestCase):
    
    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'doc1')
        self.menu = getUtility(IBrowserMenu, name='plone.contentmenu.workflow.menu', context=self.folder)
        self.request = self.app.REQUEST

    def testMenuImplementsIBrowserMenu(self):
        self.failUnless(IBrowserMenu.providedBy(self.menu))
    
    def testMenuImplementsIActionsMenu(self):
        self.failUnless(IWorkflowMenu.providedBy(self.menu))
        
    def testMenuIncludesActions(self):
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        self.failUnless('workflow-transition-submit' in
                        [a['extra']['id'] for a in actions])
        
    def testNoTransitions(self):
        self.logout()
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        self.assertEqual(len(actions), 0)
        
    def testAdvancedIncluded(self):
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        url = self.folder.doc1.absolute_url() + '/content_status_history'
        self.failUnless(url in [a['action'] for a in actions])
        
    def testPolicyIncluded(self):
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        url = self.folder.doc1.absolute_url() + '/placeful_workflow_configuration'
        self.failUnless(url in [a['action'] for a in actions])

class TestContentMenu(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.menu = getUtility(IBrowserMenu, name='plone.contentmenu', context=self.folder)
        self.request = self.app.REQUEST
        
    # Actions sub-menu
        
    def testActionsSubMenuIncluded(self):
        items = self.menu.getMenuItems(self.folder, self.request)
        actionsMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-actions'][0]
        self.assertEqual(actionsMenuItem['action'], self.folder.absolute_url() + '/folder_contents')
        self.failUnless(len(actionsMenuItem['submenu']) > 0)

    # Display sub-menu

    def testDisplayMenuIncluded(self):
        items = self.menu.getMenuItems(self.folder, self.request)
        displayMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-display'][0]
        self.assertEqual(displayMenuItem['action'], self.folder.absolute_url() + '/select_default_view')
        self.failUnless(len(displayMenuItem['submenu']) > 0)
    
    def testDisplayMenuNotIncludedIfContextDoesNotSupportBrowserDefault(self):
        # We need to create an object that does not have IBrowserDefault enabled
        _createObjectByType('CMF Folder', self.folder, 'f1')
        items = self.menu.getMenuItems(self.folder.f1, self.request)
        self.assertEqual([i for i in items if i['extra']['id'] == 'plone-contentmenu-display'], [])
    
    def testDisplayMenuNotIncludedIfNoActionsAvailable(self):
        self.folder.invokeFactory('Document', 'doc1')
        items = self.menu.getMenuItems(self.folder.doc1, self.request)
        self.assertEqual([i for i in items if i['extra']['id'] == 'plone-contentmenu-display'], [])
        
    def testDisplayMenuDisabledIfIndexHtmlInFolder(self):
        self.folder.invokeFactory('Document', 'index_html')
        items = self.menu.getMenuItems(self.folder, self.request)
        displayMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-display'][0]
        self.assertEqual(displayMenuItem['extra']['disabled'], True)
        
    def testDisplayMenuDisabledIfIndexHtmlInFolderAndContextIsIndexHtml(self):
        self.folder.invokeFactory('Document', 'index_html')
        items = self.menu.getMenuItems(self.folder.index_html, self.request)
        displayMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-display'][0]
        self.assertEqual(displayMenuItem['extra']['disabled'], True)
                
    # Add sub-menu
    
    def testAddMenuIncluded(self):
        items = self.menu.getMenuItems(self.folder, self.request)
        factoriesMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-factories'][0]
        self.assertEqual(factoriesMenuItem['action'], self.folder.absolute_url() + '/folder_factories')
        self.failUnless(len(factoriesMenuItem['submenu']) > 0)
        self.assertEqual(factoriesMenuItem['extra']['hideChildren'], False)
        
    def testAddMenuNotIncludedIfNothingToAdd(self):
        self.logout()
        items = self.menu.getMenuItems(self.folder, self.request)
        self.assertEqual([i for i in items if i['extra']['id'] == 'plone-contentmenu-factories'], [])

    def testAddMenuWithNothingToAddButWithAvailableConstrainSettings(self):
        self.folder.setConstrainTypesMode(1)
        self.folder.setLocallyAllowedTypes(())
        self.folder.setImmediatelyAddableTypes(())
        items = self.menu.getMenuItems(self.folder, self.request)
        factoriesMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-factories'][0]
        self.assertEqual(len(factoriesMenuItem['submenu']), 1)
        self.assertEqual(factoriesMenuItem['submenu'][0]['extra']['id'], '_settings')
        
    def testAddMenuWithNothingToAddButWithAvailableMorePage(self):
        self.folder.setConstrainTypesMode(1)
        self.folder.setLocallyAllowedTypes(('Document',))
        self.folder.setImmediatelyAddableTypes(())
        self.folder.manage_permission('Modify constrain types', ('Manager',))
        items = self.menu.getMenuItems(self.folder, self.request)
        factoriesMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-factories'][0]
        self.assertEqual(len(factoriesMenuItem['submenu']), 1)
        self.assertEqual(factoriesMenuItem['submenu'][0]['extra']['id'], '_more')

    def testAddMenuRelativeToNonStructuralFolder(self):
        self.folder.invokeFactory('Folder', 'f1')
        directlyProvides(self.folder.f1, INonStructuralFolder)
        items = self.menu.getMenuItems(self.folder.f1, self.request)
        factoriesMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-factories'][0]
        self.assertEqual(factoriesMenuItem['action'], self.folder.absolute_url() + '/folder_factories')
    
    def testAddMenuWithSingleItemCollapses(self):
        # we need a dummy to test this - should test that if the item does not
        # support constrain types and there is 
        self.folder.setConstrainTypesMode(1)
        self.folder.setLocallyAllowedTypes(('Document',))
        self.folder.setImmediatelyAddableTypes(('Document',))
        self.folder.manage_permission('Modify constrain types', ('Manager',))
        items = self.menu.getMenuItems(self.folder, self.request)
        factoriesMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-factories'][0]
        self.assertEqual(factoriesMenuItem['action'], self.folder.absolute_url() + '/createObject?type_name=Document')
        self.assertEqual(factoriesMenuItem['extra']['hideChildren'], True)
        
    # Workflow sub-menu
    
    def testWorkflowMenuIncluded(self):
        items = self.menu.getMenuItems(self.folder, self.request)
        workflowMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-workflow'][0]
        self.assertEqual(workflowMenuItem['action'], self.folder.absolute_url() + '/content_status_history')
        self.failUnless(len(workflowMenuItem['submenu']) > 0)
    
    def testWorkflowMenuWithNoTransitionsDisabled(self):
        self.logout()
        items = self.menu.getMenuItems(self.folder, self.request)
        workflowMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-workflow'][0]
        self.assertEqual(workflowMenuItem['action'], '')

    # XXX: Unable to write a proper test so far
    def DISABLED_testWorkflowMenuWithNoTransitionsEnabledAsManager(self):
        # set workflow guard condition that fails, so there are no transitions.
        # then show that manager will get a drop-down with settings whilst
        # regular users won't
        
        self.portal.portal_workflow.doActionFor(self.folder, 'hide')
        wf = self.portal.portal_workflow['folder_workflow']
        wf.transitions['show'].guard.expr = Expression('python: False')
        wf.transitions['publish'].guard.expr = Expression('python: False')
        
        items = self.menu.getMenuItems(self.folder, self.request)
        workflowMenuItem = [i for i in items if i['extra']['id'] == 'plone-contentmenu-workflow'][0]
        
        # A regular user doesn't see any actions
        self.failUnless(workflowMenuItem['action'] == '')
        self.failUnless(workflowMenuItem['submenu'] is None)

        self.fail('Unable to write a proper test so far')

    def testWorkflowMenuWithNoWorkflowNotIncluded(self):
        self.portal.portal_workflow.setChainForPortalTypes(('Document',), ())
        self.folder.invokeFactory('Document', 'doc1')
        actions = self.menu.getMenuItems(self.folder.doc1, self.request)
        self.failIf('plone.contentmenu.workflow.menu' in [a['extra']['id'] for a in actions])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestActionsMenu))
    suite.addTest(makeSuite(TestDisplayMenu))
    suite.addTest(makeSuite(TestFactoriesMenu))
    suite.addTest(makeSuite(TestWorkflowMenu))
    suite.addTest(makeSuite(TestContentMenu))
    return suite

if __name__ == '__main__':
    framework()
