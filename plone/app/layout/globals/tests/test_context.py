from plone.app.layout.globals.tests.base import GlobalsTestCase

from zope.interface import directlyProvides
from Products.CMFPlone.interfaces import INonStructuralFolder

from plone.locking.interfaces import ILockable


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
        self.assertEquals(self.fview.current_page_url(), url + '?foo=bar')
        
    def test_current_base_url(self):
        url = self.folder.absolute_url() + '/some_view'
        self.app.REQUEST['ACTUAL_URL'] = url
        self.app.REQUEST['QUERY_STRING'] = 'foo=bar'
        self.assertEquals(self.fview.current_base_url(), url)
        
    def test_canonical_object(self):
        self.assertEquals(self.fview.canonical_object(), self.folder)
        self.assertEquals(self.dview.canonical_object(), self.folder)
        
    def test_canonical_object_url(self):
        self.assertEquals(self.fview.canonical_object_url(), self.folder.absolute_url())
        self.assertEquals(self.dview.canonical_object_url(), self.folder.absolute_url())
        
    def test_view_url(self):
        self.assertEquals(self.fview.view_url(),
                          self.folder.absolute_url())
        self.assertEquals(self.dview.view_url(),
                          self.folder.d1.absolute_url())
        self.folder.invokeFactory('File', 'file1')
        self.fileview = self.folder.file1.restrictedTraverse('@@plone_context_state')
        self.assertEquals(self.fileview.view_url(),
                          self.folder.file1.absolute_url() + '/view')
                            
    def test_view_template_id(self):
        self.folder.setLayout('foo_view')
        self.assertEquals(self.fview.view_template_id(), 'foo_view')
                            
    def test_is_view_template_default_page(self):
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url()
        # Whether you're viewing the folder or its default page ...
        self.assertEquals(self.fview.is_view_template(), True)
        self.assertEquals(self.dview.is_view_template(), True)
        
    def test_is_view_template_trailing_slash(self):
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url() + '/'
        self.assertEquals(self.fview.is_view_template(), True)
        self.assertEquals(self.dview.is_view_template(), True)
                                    
    def test_is_view_template_template(self):
        self.folder.setLayout('foo_view')
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url() + '/foo_view'
        self.assertEquals(self.fview.is_view_template(), True)
        self.assertEquals(self.dview.is_view_template(), False)
        
    def test_is_view_template_template_z3view(self):
        self.folder.setLayout('foo_view')
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url() + '/@@foo_view'
        self.assertEquals(self.fview.is_view_template(), True)
        self.assertEquals(self.dview.is_view_template(), False)
        
    def test_is_view_template_view(self):
        self.folder.setLayout('foo_view')
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url() + '/view'
        self.assertEquals(self.fview.is_view_template(), True)
        self.assertEquals(self.dview.is_view_template(), False)
                            
    def test_is_view_template_other(self):
        self.folder.setLayout('foo_view')
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url() + '/bar_view'
        self.assertEquals(self.fview.is_view_template(), False)
        self.assertEquals(self.dview.is_view_template(), False)                            
                            
    def test_object_url(self):
        self.assertEquals(self.fview.object_url(), self.folder.absolute_url())
        self.assertEquals(self.dview.object_url(), self.folder.d1.absolute_url())
        
    def test_object_title(self):
        self.folder.d1.setTitle('My title')
        self.assertEquals(self.dview.object_title(), 'My title')
        
    def test_workflow_state(self):
        wfstate = self.portal.portal_workflow.getInfoFor(self.folder.d1, 'review_state')
        self.assertEquals(self.dview.workflow_state(), wfstate)
    
    def test_parent(self):
        self.assertEquals(self.dview.parent(), self.folder)
        self.assertEquals(self.sview.parent(), self.folder)
        
    def test_folder(self):
        self.assertEquals(self.fview.folder(), self.folder)
        self.assertEquals(self.dview.folder(), self.folder)
        self.assertEquals(self.sview.folder(), self.folder)
                            
    def test_is_folderish(self):
        self.assertEquals(self.fview.is_folderish(), True)
        self.assertEquals(self.dview.is_folderish(), False)
        self.assertEquals(self.sview.is_folderish(), True)
    
    def test_is_structural_folder(self):
        self.assertEquals(self.fview.is_structural_folder(), True)
        self.assertEquals(self.dview.is_structural_folder(), False)
        self.assertEquals(self.sview.is_structural_folder(), False)
    
    def test_is_default_page(self):
        self.assertEquals(self.fview.is_default_page(), False)
        self.assertEquals(self.dview.is_default_page(), True)
        self.assertEquals(self.sview.is_default_page(), False)
        
    def test_is_portal_root(self):
        self.assertEquals(self.fview.is_portal_root(), False)
        self.assertEquals(self.dview.is_portal_root(), False)
        self.assertEquals(self.sview.is_portal_root(), False)
        self.assertEquals(self.pview.is_portal_root(), True)
    
    def test_is_editable(self):
        self.assertEquals(self.dview.is_editable(), True)
        self.logout()
        del self.app.REQUEST.__annotations__
        self.assertEquals(self.dview.is_editable(), False)
    
    def test_is_locked(self):
        self.assertEquals(self.dview.is_locked(), False)
        ILockable(self.folder.d1).lock()
        self.logout() # The object is not "locked" if it was locked by the current user
        del self.app.REQUEST.__annotations__
        self.assertEquals(self.dview.is_locked(), True)

    def test_actions(self):
        actions = self.fview.actions('user')
        self.failUnless(actions[0]['category'] == 'user')


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
