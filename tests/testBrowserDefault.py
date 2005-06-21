#
# Test the browserDefault script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests.PloneTestCase import FunctionalTestCase
from Products.CMFPlone.tests.PloneTestCase import default_user
from Products.CMFPlone.tests.PloneTestCase import default_password
from Products.CMFPlone.tests import dummy
import difflib
import re

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.PloneFolder import ReplaceableWrapper

RE_REMOVE_DOCCONT = re.compile('href="http://.*?#documentContent"')

class TestPloneToolBrowserDefault(FunctionalTestCase):
    """Test the PloneTool's browserDefault() method in various use cases.
    This class basically tests the functionality when items have default pages
    and actions that resolve to actual objects. The cases where a default_page
    may be set to a non-existing object are covered by TestDefaultPage below.
    """
    
    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.basic_auth = '%s:%s' % (default_user, default_password)
        
        _createObjectByType('Folder',       self.portal, 'atctfolder')
        _createObjectByType('CMF Folder',   self.portal, 'cmffolder')
        _createObjectByType('Document',     self.portal, 'atctdocument')
        _createObjectByType('CMF Document', self.portal, 'cmfdocument')
        _createObjectByType('File',         self.portal, 'atctfile')
        _createObjectByType('CMF File',     self.portal, 'cmffile')
            
        self.putils = self.portal.plone_utils
    
    def compareLayoutVsView(self, obj, path="", viewaction=None):
        if viewaction is None:
            viewaction = obj.getLayout()
        resolved = getattr(obj, viewaction)()
        base_path = obj.absolute_url(1)
                
        response = self.publish(base_path+path, self.basic_auth)
        body = response.getBody()
        
        # request/ACTUAL_URL is fubar in tests, remove line that depends on it
        resolved = RE_REMOVE_DOCCONT.sub('', resolved)
        body = RE_REMOVE_DOCCONT.sub('', body)
        
        if not body == resolved:
            diff = difflib.unified_diff(body.split("\n"),
                                        resolved.split("\n"))
            self.fail("\n".join([line for line in diff]))
        return response
    
    # Folders with IBrowserDefault - default page, index_html, global default
    
    def testBrowserDefaultMixinFolderDefaultPage(self):
        self.portal.atctfolder.invokeFactory('Document', 'default')
        self.portal.atctfolder.setDefaultPage('default')
        self.assertEqual(self.putils.browserDefault(self.portal.atctfolder),
                         (self.portal.atctfolder, ['default'],))
   
    def testBrowserDefaultMixinFolderIndexHtml(self):
        self.portal.atctfolder.invokeFactory('Document', 'default')
        self.portal.atctfolder.setDefaultPage('default')
        # index_html should always win - it's an explicit override!
        self.portal.atctfolder.invokeFactory('Document', 'index_html')
        self.assertEqual(self.putils.browserDefault(self.portal.atctfolder),
                         (self.portal.atctfolder, ['index_html'],))
        
    def testBrowserDefaultMixinFolderGlobalDefaultPage(self):
        self.portal.portal_properties.site_properties.manage_changeProperties(default_page = ['foo'])
        self.portal.atctfolder.invokeFactory('Document', 'foo')
        self.assertEqual(self.putils.browserDefault(self.portal.atctfolder),
                         (self.portal.atctfolder, ['foo']))
            
    # Folders without IBrowserDefault - index_html, default_page, global default
        
    def testNonBrowserDefaultMixinFolderDefaultPageProperty(self):
        self.portal.cmffolder.invokeFactory('Document', 'foo')
        self.portal.cmffolder.manage_addProperty('default_page', 'foo', 'string')
        self.assertEqual(self.putils.browserDefault(self.portal.cmffolder),
                         (self.portal.cmffolder, ['foo'],))
        
    def testNonBrowserDefaultMixinFolderIndexHtml(self):
        self.portal.cmffolder.manage_addProperty('default_page', 'foo', 'string')
        self.portal.cmffolder.invokeFactory('Document', 'foo')
        # Again, index_html always wins!
        self.portal.cmffolder.invokeFactory('Document', 'index_html')
        self.assertEqual(self.putils.browserDefault(self.portal.cmffolder),
                         (self.portal.cmffolder, ['index_html'],))
    
    def testNonBrowserDefaultMixinFolderGlobalDefaultPage(self):
        self.portal.portal_properties.site_properties.manage_changeProperties(default_page = ['foo'])
        self.portal.cmffolder.invokeFactory('Document', 'foo')
        self.assertEqual(self.putils.browserDefault(self.portal.cmffolder),
                         (self.portal.cmffolder, ['foo']))
    
    # folderlisting action resolution (for folders without default pages)
    
    def testBrowserDefaultMixinFolderFolderlistingAction(self):
        viewAction = self.portal.portal_types['Folder'].getActionById('folderlisting')
        self.assertEqual(self.putils.browserDefault(self.portal.atctfolder),
                         (self.portal.atctfolder, [viewAction]))
        
    def testNoneBrowserDefaultMixinFolderFolderlistingAction(self):
        viewAction = self.portal.portal_types['CMF Folder'].getActionById('folderlisting')
        self.assertEqual(self.putils.browserDefault(self.portal.cmffolder),
                         (self.portal.cmffolder, [viewAction]))    
    
    # View action resolution (last fallback)
    
    def testViewMethodWithBrowserDefaultMixinGetsSelectedLayout(self):
        self.compareLayoutVsView(self.portal.atctdocument, path="/view")
        
    def testViewMethodWithoutBrowserDefaultMixinGetsViewAction(self):
        viewAction = self.portal.portal_types['CMF Document'].getActionById('view')
        obj = self.portal.cmfdocument
        self.compareLayoutVsView(self.portal.cmfdocument, path="/view",
                                 viewaction=viewAction)
        
    def testCallWithBrowserDefaultMixinGetsSelectedLayout(self):
        self.compareLayoutVsView(self.portal.atctdocument, path="")
        
    def testCallWithoutBrowserDefaultMixinGetsViewAction(self):
        viewAction = self.portal.portal_types['CMF Document'].getActionById('view')
        obj = self.portal.cmfdocument
        self.compareLayoutVsView(self.portal.cmfdocument, path="",
                                 viewaction=viewAction)
    
    # Dump data from file objects (via index_html), but get template when explicitly called
            
    def testBrowserDefaultMixinFileViewMethodGetsTemplate(self):
        self.compareLayoutVsView(self.portal.atctfile, path="/view")
        
    def testNonBrowserDefaultMixinFileViewMethodGetsTemplateFromViewAction(self):
        obj = self.portal.atctfile
        response = self.compareLayoutVsView(obj, path="",
                                            viewaction="index_html")
        self.failUnlessEqual(response.getBody(), str(obj.getFile()))
        
    # Ensure index_html acquisition and replaceablewrapper
    
    def testIndexHtmlNotAcquired(self):
        self.portal.atctfolder.invokeFactory('Document', 'index_html')
        self.portal.atctfolder.invokeFactory('Folder', 'subfolder')
        viewAction = self.portal.portal_types['Folder'].getActionById('folderlisting')
        self.assertEqual(self.putils.browserDefault(self.portal.atctfolder.subfolder),
                         (self.portal.atctfolder.subfolder, [viewAction]))
        
    def testIndexHtmlReplaceableWrapper(self):
        self.portal.atctdocument.index_html = ReplaceableWrapper(None)
        viewAction = self.portal.portal_types['Document'].getActionById('view')
        self.assertEqual(self.putils.browserDefault(self.portal.atctdocument),
                         (self.portal.atctdocument, [viewAction]))
        

class TestDefaultPage(PloneTestCase.PloneTestCase):
    """Test the default_page functionality in more detail
    """

    def afterSetUp(self):
        self.ob = dummy.DefaultPage()
        sp = self.portal.portal_properties.site_properties
        self.default = sp.getProperty('default_page', [])

    def getDefault(self):
        return self.portal.plone_utils.browserDefault(self.ob)

    def testDefaultPageSetting(self):
        self.assertEquals(self.default, ('index_html', 'index.html',
                                         'index.htm', 'FrontPage'))

    def testDefaultPageStringExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default('test', 1)
        self.assertEquals(self.getDefault(), (self.ob, ['test']))

    def testDefaultPageStringNotExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default('test', 0)
        self.assertEquals(self.getDefault(), (self.ob, ['index_html']))

    def testDefaultPageSequenceExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default(['test'], 1)
        self.assertEquals(self.getDefault(), (self.ob, ['test']))

    def testDefaultPageSequenceNotExist(self):
        # Test for https://plone.org/collector/2671
        self.ob.set_default(['test'], 0)
        self.assertEquals(self.getDefault(), (self.ob, ['index_html']))
        self.ob.keys = ['index.html']
        self.assertEquals(self.getDefault(), (self.ob, ['index.html']))
        self.ob.keys = ['index.htm']
        self.assertEquals(self.getDefault(), (self.ob, ['index.htm']))
        self.ob.keys = ['FrontPage']
        self.assertEquals(self.getDefault(), (self.ob, ['FrontPage']))

    def testBrowserDefaultPage(self):
        # Test assumes ATContentTypes + BrowserDefaultMixin
        self.folder.invokeFactory('Document', 'd1', title='document 1')
        self.folder.setDefaultPage('d1')
        self.assertEquals(self.portal.plone_utils.browserDefault(self.folder),
                            (self.folder, ['d1']))

class TestPropertyManagedBrowserDefault(PloneTestCase.PloneTestCase):
    """Test the PropertyManagedBrowserDefault mixin class, implemented by
    the root portal object
    """
    
    def afterSetUp(self):
        self.setRoles(['Manager'])
        
        # Make sure we have the front page; the portal generator should take 
        # care of this, but let's not be dependent on that in the test
        if not 'front-page' in self.portal.objectIds():
            self.portal.invokeFactory('Document', 'front-page',
                                      title = 'Welcome to Plone')
        self.portal.setDefaultPage('front-page')
    
        # Also make sure we have folder_listing and news_listing as templates
        self.portal.manage_changeProperties(selectable_views = ['folder_listing',
                                                                'news_listing'])
            
    def testCall(self):
        self.portal.setLayout('news_listing')
        resolved = self.portal()
        target = self.portal.unrestrictedTraverse('news_listing')()
        self.assertEqual(resolved, target)
            
    def testDefaultViews(self):
        self.assertEqual(self.portal.getLayout(), 'folder_listing')
        self.assertEqual(self.portal.getDefaultPage(), 'front-page')
        self.assertEqual(self.portal.defaultView(), 'front-page')
        self.assertEqual(self.portal.getDefaultLayout(), 'folder_listing')
        layoutKeys = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless('folder_listing' in layoutKeys)
        self.failUnless('news_listing' in layoutKeys)
        self.assertEqual(self.portal.__browser_default__(None), (self.portal, ['front-page',]))
        
    def testCanSetLayout(self):
        self.failUnless(self.portal.canSetLayout())
        self.portal.manage_permission('Modify portal content', [], 0)
        self.failIf(self.portal.canSetLayout()) # Not permitted
    
    def testSetLayout(self):
        self.portal.setLayout('news_listing')
        self.assertEqual(self.portal.getLayout(), 'news_listing')
        self.assertEqual(self.portal.getDefaultPage(), None)
        self.assertEqual(self.portal.defaultView(), 'news_listing')
        self.assertEqual(self.portal.getDefaultLayout(), 'folder_listing')
        layoutKeys = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless('folder_listing' in layoutKeys)
        self.failUnless('news_listing' in layoutKeys)
        
        view = self.portal.view()
        browserDefault = self.portal.__browser_default__(None)[1][0]
        browserDefaultResolved = self.portal.unrestrictedTraverse(browserDefault)()
        template = self.portal.defaultView()
        templateResolved = self.portal.unrestrictedTraverse(template)()
        
        self.assertEqual(view, browserDefaultResolved)
        self.assertEqual(view, templateResolved)
        
    def testCanSetDefaultPage(self):
        self.failUnless(self.portal.canSetDefaultPage())
        self.portal.invokeFactory('Document', 'ad')
        self.failIf(self.portal.ad.canSetDefaultPage()) # Not folderish
        self.portal.manage_permission('Modify portal content', [], 0)
        self.failIf(self.portal.canSetDefaultPage()) # Not permitted
        
    def testSetDefaultPage(self):
        self.portal.invokeFactory('Document', 'ad')
        self.portal.setDefaultPage('ad')
        self.assertEqual(self.portal.getDefaultPage(), 'ad')
        self.assertEqual(self.portal.defaultView(), 'ad')
        self.assertEqual(self.portal.__browser_default__(None), (self.portal, ['ad',]))
        
        # still have layout settings
        self.assertEqual(self.portal.getLayout(), 'folder_listing')
        self.assertEqual(self.portal.getDefaultLayout(), 'folder_listing')
        layoutKeys = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless('folder_listing' in layoutKeys)
        self.failUnless('news_listing' in layoutKeys)
    
    def testSetLayoutUnsetsDefaultPage(self):
        self.portal.invokeFactory('Document', 'ad')
        self.portal.setDefaultPage('ad')
        self.assertEqual(self.portal.getDefaultPage(), 'ad')
        self.assertEqual(self.portal.defaultView(), 'ad')
        self.portal.setLayout('folder_listing')
        self.assertEqual(self.portal.getDefaultPage(), None)
        self.assertEqual(self.portal.defaultView(), 'folder_listing')
        
        view = self.portal.view()
        browserDefault = self.portal.__browser_default__(None)[1][0]
        browserDefaultResolved = self.portal.unrestrictedTraverse(browserDefault)()
        template = self.portal.defaultView()
        templateResolved = self.portal.unrestrictedTraverse(template)()
        
        self.assertEqual(view, browserDefaultResolved)
        self.assertEqual(view, templateResolved)

    def testMissingTemplatesIgnored(self):
        self.portal.manage_changeProperties(selectable_views = ['folder_listing', 'foo'])
        views = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless(views == ['folder_listing'])

    def testTemplateTitles(self):
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        self.assertEqual(views[0][1], 'Standard listing')
        folderListing = self.portal.unrestrictedTraverse('folder_listing')
        folderListing.title = 'foo'
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        self.assertEqual(views[0][1], 'foo')
    


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneToolBrowserDefault))
    suite.addTest(makeSuite(TestDefaultPage))
    suite.addTest(makeSuite(TestPropertyManagedBrowserDefault))
    return suite

if __name__ == '__main__':
    framework()
