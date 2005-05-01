#
# Test the browserDefault script
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy


class TestDefaultPage(PloneTestCase.PloneTestCase):

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

    def testBrowserDefaultLayout(self):
        # Test assumes ATContentTypes + BrowserDefaultMixin + atct_album_view
        self.folder.setLayout('atct_album_view')
        self.assertEquals(self.portal.plone_utils.browserDefault(self.folder), 
                            (self.folder, ['atct_album_view']))

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
        
        # We mangle the title here for testing, but somehow the change seems
        # to persiste between tests. Make sure it's reset properly.
        folderListing = self.portal.unrestrictedTraverse('folder_listing')
        folderListing.title = 'Folder listing'
    
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
        self.assertEqual(self.portal.__browser_default__(None), (self.portal, ['news_listing',]))
        
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
        self.assertEqual(self.portal.__browser_default__(None), (self.portal, ['folder_listing',]))

    def testMissingTemplatesIgnored(self):
        self.portal.manage_changeProperties(selectable_views = ['folder_listing', 'foo'])
        views = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless(views == ['folder_listing'])

    def testTemplateTitles(self):
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        self.assertEqual(views[0][1], 'Folder listing')
                
    def testTitleCache(self):
        self.portal.invalidateSelectableViewsCache() # Make sure the cache is fresh
        folderListing = self.portal.unrestrictedTraverse('folder_listing')
        folderListing.title = 'foo'        
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        # Cached
        self.assertEqual(views[0][1], 'Folder listing')
        
    def testTitleCacheExplicitlyInvalidated(self):
        self.portal.invalidateSelectableViewsCache() # Make sure the cache is fresh
        folderListing = self.portal.unrestrictedTraverse('folder_listing')
        folderListing.title = 'foo'
        self.portal.invalidateSelectableViewsCache()
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        self.assertEqual(views[0][1], 'foo')
        
    def testTitleCacheImplicitlyInvalidatedByNewView(self):
        self.portal.invalidateSelectableViewsCache() # Make sure the cache is fresh
        folderListing = self.portal.unrestrictedTraverse('folder_listing')
        folderListing.title = 'foo'
        self.portal.manage_changeProperties(selectable_views = ['folder_listing',
                                                                'news_listing',
                                                                'folder_contents'])
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        self.assertEqual(views[0][1], 'foo')
    
    def testTitleCacheImplicitlyInvalidatedByRemovingView(self):
        self.portal.invalidateSelectableViewsCache() # Make sure the cache is fresh
        folderListing = self.portal.unrestrictedTraverse('folder_listing')
        folderListing.title = 'foo'
        self.portal.manage_changeProperties(selectable_views = ['folder_listing'])
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        self.assertEqual(views[0][1], 'foo')
        
    def testTitleCacheImplicitlyInvalidatedByChangingView(self):
        self.portal.invalidateSelectableViewsCache() # Make sure the cache is fresh
        folderListing = self.portal.unrestrictedTraverse('folder_listing')
        folderListing.title = 'foo'
        self.portal.manage_changeProperties(selectable_views = ['folder_listing',
                                                                'folder_contents'])
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        self.assertEqual(views[0][1], 'foo')
        
    def testMissingTemplatesIgnoredAfterCacheInvalidation(self):
        self.portal.invalidateSelectableViewsCache() # Make sure the cache is fresh
        self.portal.manage_changeProperties(selectable_views = ['folder_listing', 'foo'])
        folderListing = self.portal.unrestrictedTraverse('folder_listing')
        folderListing.title = 'foo'
        self.portal.invalidateSelectableViewsCache()
        views = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless(views == ['folder_listing'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDefaultPage))
    suite.addTest(makeSuite(TestPropertyManagedBrowserDefault))
    return suite

if __name__ == '__main__':
    framework()
