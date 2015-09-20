from Acquisition import aq_base
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import setRoles
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.PloneFolder import ReplaceableWrapper
from zope.component import getUtility
import difflib
import re
import transaction
import unittest2 as unittest

RE_REMOVE_DOCCONT = re.compile('\s*href="http://.*?#content"')
RE_REMOVE_SKIPNAV = re.compile('\s*href="http://.*?#portal-globalnav-wrapper"')
RE_REMOVE_TABS = re.compile('<div id="portal-header".*?</nav>', re.S)
RE_REMOVE_AUTH = re.compile('\_authenticator\=.*?\"', re.S)


class TestPloneToolBrowserDefault(unittest.TestCase):
    """Test the PloneTool's browserDefault() method in various use cases.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # disable diazo theming
        self.portal.portal_registry[
            'plone.app.theming.interfaces.IThemeSettings.enabled'
        ] = False

        # disable auto-CSRF
        from plone.protect import auto
        auto.CSRF_DISABLED = True

        _createObjectByType('Folder', self.portal, 'folder')
        _createObjectByType('Document', self.portal, 'document')
        _createObjectByType('File', self.portal, 'file')
        self.portal.file.file = NamedBlobFile('foo', 'text/plain', u'foo.txt')
        transaction.commit()

        self.putils = getToolByName(self.portal, "plone_utils")
        self.browser = Browser(self.layer['app'])
        self.browser.addHeader(
            'Authorization', 'Basic %s:%s' % (
                TEST_USER_NAME,
                TEST_USER_PASSWORD,
            )
        )

    def tearDown(self):
        from plone.protect import auto
        auto.CSRF_DISABLED = False

    def compareLayoutVsView(self, obj, path="", viewaction=None):
        if viewaction is None:
            if hasattr(aq_base(obj), 'getLayout'):
                viewaction = obj.getLayout()
            else:
                viewaction = obj.getTypeInfo().getActionInfo(
                    'object/view'
                )['url'].split('/')[-1]

        self.layer['app'].REQUEST['ACTUAL_URL'] = obj.absolute_url()
        resolved = obj.restrictedTraverse(viewaction)()

        # rendering the view cooked the resource registry,
        # so commit the transaction so loading it via the testbrowser
        # doesn't cook it again
        transaction.commit()

        self.browser.open(obj.absolute_url() + path)
        body = self.browser.contents.decode('utf8')

        # request/ACTUAL_URL is fubar in tests, remove lines that depend on it
        resolved = RE_REMOVE_DOCCONT.sub('', resolved)
        resolved = RE_REMOVE_SKIPNAV.sub('', resolved)
        resolved = RE_REMOVE_TABS.sub('', resolved)
        resolved = RE_REMOVE_AUTH.sub('"', resolved)

        body = RE_REMOVE_DOCCONT.sub('', body)
        body = RE_REMOVE_SKIPNAV.sub('', body)
        body = RE_REMOVE_TABS.sub('', body)
        body = RE_REMOVE_AUTH.sub('"', body)

        if not body:
            self.fail('No body in response')

        if not body == resolved:
            diff = difflib.unified_diff(body.split("\n"),
                                        resolved.split("\n"))
            self.fail("\n".join([line for line in diff]))

    def compareLayoutVsCall(self, obj):
        if hasattr(aq_base(obj), 'getLayout'):
            viewaction = obj.getLayout()
        else:
            viewaction = obj.getTypeInfo().getActionInfo(
                'object/view')['url'].split('/')[-1]

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
        self.portal.folder.invokeFactory('Document', 'default')
        self.portal.folder.setDefaultPage('default')
        self.assertEqual(self.putils.browserDefault(self.portal.folder),
                         (self.portal.folder, ['default'],))

    def testBrowserDefaultMixinFolderIndexHtml(self):
        self.portal.folder.invokeFactory('Document', 'default')
        self.portal.folder.setDefaultPage('default')
        # index_html should always win - it's an explicit override!
        self.portal.folder.invokeFactory('Document', 'index_html')
        self.assertEqual(self.putils.browserDefault(self.portal.folder),
                         (self.portal.folder, ['index_html'],))

    def testBrowserDefaultMixinFolderGlobalDefaultPage(self):
        registry = getUtility(IRegistry)
        registry['plone.default_page'] = [u'foo']
        self.portal.folder.invokeFactory('Document', 'foo')
        self.assertEqual(self.putils.browserDefault(self.portal.folder),
                         (self.portal.folder, ['foo']))

    # View action resolution (last fallback)

    def testViewMethodWithBrowserDefaultMixinGetsSelectedLayout(self):
        self.compareLayoutVsView(self.portal.document, path="/view")

    def testCallWithBrowserDefaultMixinGetsSelectedLayout(self):
        self.compareLayoutVsView(self.portal.document, path="")

    # Dump data from file objects (via index_html), but get template when
    # explicitly called

    def testBrowserDefaultMixinFileViewMethodGetsTemplate(self):
        self.compareLayoutVsView(self.portal.file, path="/view")

    def testBrowserDefaultMixinFileDumpsContent(self):
        self.browser.open(self.portal.file.absolute_url())
        self.assertEqual(self.browser.contents, self.portal.file.file.data)

    # Ensure index_html acquisition and replaceablewrapper

    def testIndexHtmlNotAcquired(self):
        self.portal.folder.invokeFactory('Document', 'index_html')
        self.portal.folder.invokeFactory('Folder', 'subfolder')
        layout = self.portal.folder.getLayout()
        self.assertEqual(
            self.putils.browserDefault(self.portal.folder.subfolder),
            (self.portal.folder.subfolder, [layout])
        )

    def testIndexHtmlReplaceableWrapper(self):
        self.portal.document.index_html = ReplaceableWrapper(None)
        layout = self.portal.document.getLayout()
        self.assertEqual(self.putils.browserDefault(self.portal.document),
                         (self.portal.document, [layout]))

    # Test behaviour of __call__

    def testCallDocumentGivesTemplate(self):
        self.compareLayoutVsCall(self.portal.document)

    def testCallFolderWithoutDefaultPageGivesTemplate(self):
        self.compareLayoutVsCall(self.portal.folder)

    def testCallFolderWithDefaultPageGivesTemplate(self):
        self.portal.folder.invokeFactory('Document', 'doc')
        self.portal.folder.setDefaultPage('doc')
        self.compareLayoutVsCall(self.portal.folder)

    def testCallFileGivesTemplate(self):
        self.compareLayoutVsCall(self.portal.file)

    # Tests for strange bugs...

    def testReselectingDefaultLayoutAfterDefaultPageWorks(self):
        defaultLayout = self.portal.folder.getDefaultLayout()
        self.portal.folder.invokeFactory('Document', 'default')
        self.portal.folder.setDefaultPage('default')
        self.portal.folder.setLayout(defaultLayout)
        self.assertEqual(self.portal.folder.getDefaultPage(), None)
        self.assertEqual(self.portal.folder.defaultView(), defaultLayout)

    def testBrowserDefaultMixinWithoutFtiGivesSensibleError(self):
        # Test for issue http://dev.plone.org/plone/ticket/5676
        # Ensure that the error displayed for missing FTIs is not so cryptic
        getToolByName(self.portal, "portal_types")._delOb('Document')

        self.assertRaises(AttributeError,
                          self.portal.plone_utils.browserDefault,
                          self.portal.document)

    def testFolderDefaultPageSameAsSelfWithPageMissing(self):
        # We need to avoid infinite recursion in the case that
        # a page with the same id as the folder was made the default
        # page and then deleted. See http://dev.plone.org/plone/ticket/5704
        # We should fallback on the default layout folder_listing
        f = self.portal.folder
        f.invokeFactory('Document', f.getId())
        f.setDefaultPage(f.getId())
        self.assertEqual(self.putils.browserDefault(f),
                         (f, [f.getId()],))
        f._delObject(f.getId())
        self.assertTrue(
            self.putils.browserDefault(f) == (f, ['folder_listing'],)
            or
            self.putils.browserDefault(f) == (f, ['listing_view'],)
            # plone.app.contenttypes has unified views
        )

    def testDefaultPageSetting(self):
        registry = getUtility(IRegistry)
        default = registry.get('plone.default_page', [])
        self.assertEqual(
            default,
            [u'index_html', u'index.html', u'index.htm', u'FrontPage']
            )


class TestPortalBrowserDefault(unittest.TestCase):
    """Test the BrowserDefaultMixin as implemented by the root portal object
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Make sure we have the front page; the portal generator should take
        # care of this, but let's not be dependent on that in the test
        if not 'front-page' in self.portal.objectIds():
            self.portal.invokeFactory('Document', 'front-page',
                                      title='Welcome to Plone')
        self.portal.setDefaultPage('front-page')

    def assertFalseDiff(self, text1, text2):
        """
        Compare two bodies of text.  If they are not the same, fail and output
        the diff
        """
        if text1 != text2:
            diff = difflib.unified_diff(text1.split("\n"), text2.split("\n"))
            self.fail("\n".join([line for line in diff]))

    def testCall(self):
        self.portal.setLayout('folder_listing')
        resolved = self.portal()
        target = self.portal.unrestrictedTraverse('folder_listing')()
        self.assertFalseDiff(resolved, target)

    def testDefaultViews(self):
        self.assertEqual(self.portal.getLayout(), 'listing_view')
        self.assertEqual(self.portal.getDefaultPage(), 'front-page')
        self.assertEqual(self.portal.defaultView(), 'front-page')
        self.assertEqual(self.portal.getDefaultLayout(), 'listing_view')
        layoutKeys = [v[0] for v in self.portal.getAvailableLayouts()]
        self.assertTrue('listing_view' in layoutKeys)
        self.assertEqual(self.portal.__browser_default__(None),
                         (self.portal, ['front-page', ]))

    def testCanSetLayout(self):
        self.assertTrue(self.portal.canSetLayout())
        self.portal.manage_permission("Modify view template", [], 0)
        self.assertFalse(self.portal.canSetLayout())  # Not permitted

    def testSetLayout(self):
        self.portal.setLayout('summary_view')
        self.assertEqual(self.portal.getLayout(), 'summary_view')
        self.assertEqual(self.portal.getDefaultPage(), None)
        self.assertEqual(self.portal.defaultView(), 'summary_view')
        self.assertEqual(self.portal.getDefaultLayout(), 'listing_view')
        layoutKeys = [v[0] for v in self.portal.getAvailableLayouts()]
        self.assertTrue('summary_view' in layoutKeys)

        view = self.portal.view()
        browserDefault = self.portal.__browser_default__(None)[1][0]
        browserDefaultResolved = \
            self.portal.unrestrictedTraverse(browserDefault)()
        template = self.portal.defaultView()
        templateResolved = self.portal.unrestrictedTraverse(template)()

        self.assertFalseDiff(view, browserDefaultResolved)
        self.assertFalseDiff(view, templateResolved)

    def testCanSetDefaultPage(self):
        self.assertTrue(self.portal.canSetDefaultPage())
        self.portal.invokeFactory('Document', 'ad')
        self.assertFalse(self.portal.ad.canSetDefaultPage())  # Not folderish
        self.portal.manage_permission("Modify view template", [], 0)
        self.assertFalse(self.portal.canSetDefaultPage())  # Not permitted

    def testSetDefaultPage(self):
        self.portal.invokeFactory('Document', 'ad')
        self.portal.setDefaultPage('ad')
        self.assertEqual(self.portal.getDefaultPage(), 'ad')
        self.assertEqual(self.portal.defaultView(), 'ad')
        self.assertEqual(self.portal.__browser_default__(None),
                         (self.portal, ['ad', ]))

        # still have layout settings
        self.assertEqual(self.portal.getLayout(), 'listing_view')
        self.assertEqual(self.portal.getDefaultLayout(), 'listing_view')
        layoutKeys = [v[0] for v in self.portal.getAvailableLayouts()]
        self.assertTrue('listing_view' in layoutKeys)

    def testSetDefaultPageUpdatesCatalog(self):
        # Ensure that Default page changes update the catalog
        cat = getToolByName(self.portal, "portal_catalog")
        self.portal.invokeFactory('Document', 'ad')
        self.portal.invokeFactory('Document', 'other')
        self.assertEqual(
            len(cat(getId=['ad', 'other'], is_default_page=True)), 0)
        self.portal.setDefaultPage('ad')
        self.assertEqual(
            len(cat(getId='ad', is_default_page=True)), 1)
        self.portal.setDefaultPage('other')
        self.assertEqual(
            len(cat(getId='other', is_default_page=True)), 1)
        self.assertEqual(
            len(cat(getId='ad', is_default_page=True)), 0)
        self.portal.setDefaultPage(None)
        self.assertEqual(
            len(cat(getId=['ad', 'other'], is_default_page=True)), 0)

    def testSetLayoutUnsetsDefaultPage(self):
        self.portal.invokeFactory('Document', 'ad')
        self.portal.setDefaultPage('ad')
        self.assertEqual(self.portal.getDefaultPage(), 'ad')
        self.assertEqual(self.portal.defaultView(), 'ad')
        self.portal.setLayout('folder_listing')

        self.assertFalseDiff(self.portal.getDefaultPage(), None)
        self.assertFalseDiff(self.portal.defaultView(), 'folder_listing')

        view = self.portal.view()
        browserDefault = self.portal.__browser_default__(None)[1][0]
        browserDefaultResolved = \
            self.portal.unrestrictedTraverse(browserDefault)()
        template = self.portal.defaultView()
        templateResolved = self.portal.unrestrictedTraverse(template)()

        self.assertFalseDiff(view, browserDefaultResolved)
        self.assertFalseDiff(view, templateResolved)

    def testMissingTemplatesIgnored(self):
        self.portal.getTypeInfo() \
            .manage_changeProperties(view_methods=['listing_view', 'foo'])
        views = [v[0] for v in self.portal.getAvailableLayouts()]
        self.assertTrue(views == ['listing_view'])

    def testMissingPageIgnored(self):
        self.portal.setDefaultPage('inexistent')
        self.assertEqual(self.portal.getDefaultPage(), None)
        self.assertEqual(self.portal.defaultView(), 'listing_view')
        self.assertEqual(self.portal.__browser_default__(None),
                         (self.portal, ['listing_view', ]))
