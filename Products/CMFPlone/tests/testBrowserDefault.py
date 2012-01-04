#
# Test the browserDefault script
#

from Products.CMFPlone.tests import PloneTestCase

from Products.CMFPlone.tests.PloneTestCase import default_user
from Products.CMFPlone.tests.PloneTestCase import default_password

import difflib
import re

from Acquisition import aq_base
from zope.event import notify
from zope.traversing.interfaces import BeforeTraverseEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.PloneFolder import ReplaceableWrapper

RE_REMOVE_DOCCONT = re.compile('\s*href="http://.*?#content"')
RE_REMOVE_SKIPNAV = re.compile('\s*href="http://.*?#portal-globalnav"')
RE_REMOVE_TABS = re.compile('<ul id="portal-globalnav".*?</ul>', re.S)


class TestPloneToolBrowserDefault(PloneTestCase.FunctionalTestCase):
    """Test the PloneTool's browserDefault() method in various use cases.
    This class basically tests the functionality when items have default pages
    and actions that resolve to actual objects. The cases where a default_page
    may be set to a non-existing object are covered by TestDefaultPage below.
    """

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.basic_auth = '%s:%s' % (default_user, default_password)

        # make sure the test request gets marked with the default theme layer
        notify(BeforeTraverseEvent(self.portal, self.app.REQUEST))

        _createObjectByType('Folder',       self.portal, 'atctfolder')
        _createObjectByType('Document',     self.portal, 'atctdocument')
        _createObjectByType('File',         self.portal, 'atctfile')

        self.putils = getToolByName(self.portal, "plone_utils")

    def compareLayoutVsView(self, obj, path="", viewaction=None):
        if viewaction is None:
            if hasattr(aq_base(obj), 'getLayout'):
                viewaction = obj.getLayout()
            else:
                viewaction = obj.getTypeInfo().getActionInfo('object/view')['url'].split('/')[-1]

        resolved = obj.restrictedTraverse(viewaction)()
        base_path = obj.absolute_url(1)

        response = self.publish(base_path+path, self.basic_auth)
        body = response.getBody().decode('utf-8')

        # request/ACTUAL_URL is fubar in tests, remove lines that depend on it
        resolved = RE_REMOVE_DOCCONT.sub('', resolved)
        resolved = RE_REMOVE_SKIPNAV.sub('', resolved)
        resolved = RE_REMOVE_TABS.sub('', resolved)

        body = RE_REMOVE_DOCCONT.sub('', body)
        body = RE_REMOVE_SKIPNAV.sub('', body)
        body = RE_REMOVE_TABS.sub('', body)

        if not body:
            self.fail('No body in response')

        if not body == resolved:
            diff = difflib.unified_diff(body.split("\n"),
                                        resolved.split("\n"))
            self.fail("\n".join([line for line in diff]))

        return response

    def compareLayoutVsCall(self, obj):
        if hasattr(aq_base(obj), 'getLayout'):
            viewaction = obj.getLayout()
        else:
            viewaction = obj.getTypeInfo().getActionInfo('object/view')['url'].split('/')[-1]

        base_path = obj.absolute_url(1)
        viewed = obj.restrictedTraverse(viewaction)()
        called = obj()

        # request/ACTUAL_URL is fubar in tests, remove line that depends on it
        called = RE_REMOVE_DOCCONT.sub('', called)
        viewed = RE_REMOVE_DOCCONT.sub('', viewed)

        if not called or not viewed:
            self.fail('No body in response')

        if not viewed == called:
            diff = difflib.unified_diff(viewed.split("\n"),
                                        called.split("\n"))
            self.fail("\n".join([line for line in diff]))

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
        getToolByName(self.portal, "portal_properties").site_properties.manage_changeProperties(default_page = ['foo'])
        self.portal.atctfolder.invokeFactory('Document', 'foo')
        self.assertEqual(self.putils.browserDefault(self.portal.atctfolder),
                         (self.portal.atctfolder, ['foo']))

    # View action resolution (last fallback)

    def testViewMethodWithBrowserDefaultMixinGetsSelectedLayout(self):
        self.compareLayoutVsView(self.portal.atctdocument, path="/view")

    def testCallWithBrowserDefaultMixinGetsSelectedLayout(self):
        self.compareLayoutVsView(self.portal.atctdocument, path="")

    # Dump data from file objects (via index_html), but get template when explicitly called

    def testBrowserDefaultMixinFileViewMethodGetsTemplate(self):
        self.compareLayoutVsView(self.portal.atctfile, path="/view")

    def testBrowserDefaultMixinFileDumpsContent(self):
        response = self.publish(self.portal.atctfile.absolute_url(1), self.basic_auth)
        self.failUnlessEqual(response.getBody(), str(self.portal.atctfile.getFile()))


    # Ensure index_html acquisition and replaceablewrapper

    def testIndexHtmlNotAcquired(self):
        self.portal.atctfolder.invokeFactory('Document', 'index_html')
        self.portal.atctfolder.invokeFactory('Folder', 'subfolder')
        layout = self.portal.atctfolder.getLayout()
        self.assertEqual(self.putils.browserDefault(self.portal.atctfolder.subfolder),
                         (self.portal.atctfolder.subfolder, [layout]))

    def testIndexHtmlReplaceableWrapper(self):
        self.portal.atctdocument.index_html = ReplaceableWrapper(None)
        layout = self.portal.atctdocument.getLayout()
        self.assertEqual(self.putils.browserDefault(self.portal.atctdocument),
                         (self.portal.atctdocument, [layout]))

    # Test behaviour of __call__

    def testCallDocumentGivesTemplate(self):
        self.compareLayoutVsCall(self.portal.atctdocument)

    def testCallFolderWithoutDefaultPageGivesTemplate(self):
        self.compareLayoutVsCall(self.portal.atctfolder)

    def testCallFolderWithDefaultPageGivesTemplate(self):
        self.portal.atctfolder.invokeFactory('Document', 'doc')
        self.portal.atctfolder.setDefaultPage('doc')
        self.compareLayoutVsCall(self.portal.atctfolder)

    def testCallFileGivesTemplate(self):
        self.portal.atctfolder.invokeFactory('File', 'f1')
        self.compareLayoutVsCall(self.portal.atctfolder.f1)

    # Tests for strange bugs...

    def testReselectingDefaultLayoutAfterDefaultPageWorks(self):
        defaultLayout = self.portal.atctfolder.getDefaultLayout()
        self.portal.atctfolder.invokeFactory('Document', 'default')
        self.portal.atctfolder.setDefaultPage('default')
        self.portal.atctfolder.setLayout(defaultLayout)
        self.assertEqual(self.portal.atctfolder.getDefaultPage(), None)
        self.assertEqual(self.portal.atctfolder.defaultView(), defaultLayout)

    def testBrowserDefaultMixinWithoutFtiGivesSensibleError(self):
        # Test for issue http://dev.plone.org/plone/ticket/5676
        # Ensure that the error displayed for missing FTIs is not so cryptic
        getToolByName(self.portal, "portal_types")._delOb('Document')

        self.assertRaises(AttributeError,
                          self.portal.plone_utils.browserDefault,
                          self.portal.atctdocument)

    def testFolderDefaultPageSameAsSelfWithPageMissing(self):
        # We need to avoid infinite recursion in the case that
        # a page with the same id as the folder was made the default
        # page and then deleted. See http://dev.plone.org/plone/ticket/5704
        # We should fallback on the default layout folder_listing
        f = self.portal.atctfolder
        f.invokeFactory('Document', f.getId())
        f.setDefaultPage(f.getId())
        self.assertEqual(self.putils.browserDefault(f),
                         (f, [f.getId()],))
        f._delObject(f.getId())
        self.assertEqual(self.putils.browserDefault(f),
                         (f, ['folder_listing'],))


class TestDefaultPage(PloneTestCase.PloneTestCase):
    """Test the default_page functionality in more detail
    """

    def afterSetUp(self):
        sp = getToolByName(self.portal, "portal_properties").site_properties
        self.default = sp.getProperty('default_page', [])

    def testDefaultPageSetting(self):
        self.assertEquals(self.default, ('index_html', 'index.html',
                                         'index.htm', 'FrontPage'))

    def testBrowserDefaultPage(self):
        # Test assumes ATContentTypes + BrowserDefaultMixin
        self.folder.invokeFactory('Document', 'd1', title='document 1')
        self.folder.setDefaultPage('d1')
        self.assertEquals(self.portal.plone_utils.browserDefault(self.folder),
                            (self.folder, ['d1']))

class TestPortalBrowserDefault(PloneTestCase.PloneTestCase):
    """Test the BrowserDefaultMixin as implemented by the root portal object
    """

    def afterSetUp(self):
        self.setRoles(['Manager'])

        # Make sure we have the front page; the portal generator should take
        # care of this, but let's not be dependent on that in the test
        if not 'front-page' in self.portal.objectIds():
            self.portal.invokeFactory('Document', 'front-page',
                                      title = 'Welcome to Plone')
        self.portal.setDefaultPage('front-page')

        # Also make sure we have folder_listing as a template
        self.portal.getTypeInfo().manage_changeProperties(view_methods =
                                        ['folder_listing'],
                                        default_view = 'folder_listing')

    def failIfDiff(self, text1, text2):
        """
        Compare two bodies of text.  If they are not the same, fail and output the diff
        """
        if text1 != text2:
            diff = difflib.unified_diff(text1.split("\n"), text2.split("\n"))
            self.fail("\n".join([line for line in diff]))


    def testCall(self):
        self.portal.setLayout('folder_listing')
        resolved = self.portal()
        target = self.portal.unrestrictedTraverse('folder_listing')()
        self.failIfDiff(resolved, target)

    def testDefaultViews(self):
        self.assertEqual(self.portal.getLayout(), 'folder_listing')
        self.assertEqual(self.portal.getDefaultPage(), 'front-page')
        self.assertEqual(self.portal.defaultView(), 'front-page')
        self.assertEqual(self.portal.getDefaultLayout(), 'folder_listing')
        layoutKeys = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless('folder_listing' in layoutKeys)
        self.assertEqual(self.portal.__browser_default__(None), (self.portal, ['front-page',]))

    def testCanSetLayout(self):
        self.failUnless(self.portal.canSetLayout())
        self.portal.manage_permission("Modify view template", [], 0)
        self.failIf(self.portal.canSetLayout()) # Not permitted

    def testSetLayout(self):
        self.portal.setLayout('folder_listing')
        self.assertEqual(self.portal.getLayout(), 'folder_listing')
        self.assertEqual(self.portal.getDefaultPage(), None)
        self.assertEqual(self.portal.defaultView(), 'folder_listing')
        self.assertEqual(self.portal.getDefaultLayout(), 'folder_listing')
        layoutKeys = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless('folder_listing' in layoutKeys)

        view = self.portal.view()
        browserDefault = self.portal.__browser_default__(None)[1][0]
        browserDefaultResolved = self.portal.unrestrictedTraverse(browserDefault)()
        template = self.portal.defaultView()
        templateResolved = self.portal.unrestrictedTraverse(template)()

        self.failIfDiff(view, browserDefaultResolved)
        self.failIfDiff(view, templateResolved)


    def testCanSetDefaultPage(self):
        self.failUnless(self.portal.canSetDefaultPage())
        self.portal.invokeFactory('Document', 'ad')
        self.failIf(self.portal.ad.canSetDefaultPage()) # Not folderish
        self.portal.manage_permission("Modify view template", [], 0)
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

    def testSetDefaultPageUpdatesCatalog(self):
        # Ensure that Default page changes update the catalog
        cat = getToolByName(self.portal, "portal_catalog")
        self.portal.invokeFactory('Document', 'ad')
        self.portal.invokeFactory('Document', 'other')
        self.assertEqual(len(cat(getId=['ad','other'],is_default_page=True)), 0)
        self.portal.setDefaultPage('ad')
        self.assertEqual(len(cat(getId='ad',is_default_page=True)), 1)
        self.portal.setDefaultPage('other')
        self.assertEqual(len(cat(getId='other',is_default_page=True)), 1)
        self.assertEqual(len(cat(getId='ad',is_default_page=True)), 0)
        self.portal.setDefaultPage(None)
        self.assertEqual(len(cat(getId=['ad','other'],is_default_page=True)), 0)

    def testSetLayoutUnsetsDefaultPage(self):
        self.portal.invokeFactory('Document', 'ad')
        self.portal.setDefaultPage('ad')
        self.assertEqual(self.portal.getDefaultPage(), 'ad')
        self.assertEqual(self.portal.defaultView(), 'ad')
        self.portal.setLayout('folder_listing')

        self.failIfDiff(self.portal.getDefaultPage(), None)
        self.failIfDiff(self.portal.defaultView(), 'folder_listing')

        view = self.portal.view()
        browserDefault = self.portal.__browser_default__(None)[1][0]
        browserDefaultResolved = self.portal.unrestrictedTraverse(browserDefault)()
        template = self.portal.defaultView()
        templateResolved = self.portal.unrestrictedTraverse(template)()

        self.failIfDiff(view, browserDefaultResolved)
        self.failIfDiff(view, templateResolved)

    def testMissingTemplatesIgnored(self):
        self.portal.getTypeInfo().manage_changeProperties(view_methods = ['folder_listing', 'foo'])
        views = [v[0] for v in self.portal.getAvailableLayouts()]
        self.failUnless(views == ['folder_listing'])

    def testMissingPageIgnored(self):
        self.portal.setDefaultPage('inexistent')
        self.assertEqual(self.portal.getDefaultPage(), None)
        self.assertEqual(self.portal.defaultView(), 'folder_listing')
        self.assertEqual(self.portal.__browser_default__(None), (self.portal, ['folder_listing',]))

    def testTemplateTitles(self):
        views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
        self.assertEqual(views[0][1], 'Standard view')
        try:
            folderListing = self.portal.unrestrictedTraverse('folder_listing')
            folderListing.title = 'foo'
            views = [v for v in self.portal.getAvailableLayouts() if v[0] == 'folder_listing']
            self.assertEqual(views[0][1], 'foo')
        finally:
            # Restore title to avoid side-effects
            folderListing.title = 'Standard view'


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneToolBrowserDefault))
    suite.addTest(makeSuite(TestDefaultPage))
    suite.addTest(makeSuite(TestPortalBrowserDefault))
    return suite
