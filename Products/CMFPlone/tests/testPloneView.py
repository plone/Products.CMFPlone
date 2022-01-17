from Products.CMFPlone.browser.ploneview import Plone
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests import PloneTestCase


class TestPloneView(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        self.view = Plone(self.portal, self.app.REQUEST)

    def _invalidateRequestMemoizations(self):
        try:
            del self.app.REQUEST.__annotations__
        except AttributeError:
            pass

    def testToLocalizedTime(self):
        localdate = self.view.toLocalizedTime
        value = localdate('Mar 9, 1997 1:45pm', long_format=True)
        self.assertEqual(value, 'Mar 09, 1997 01:45 PM')

    def testToLocalizedSize(self):
        tolocalsize = self.view.toLocalizedSize
        value = tolocalsize(3322)
        self.assertEqual(value, '3 KB')

    def testIsStructuralFolderWithNonFolder(self):
        i = dummy.Item()
        self.assertFalse(Plone(i, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithFolder(self):
        f = dummy.Folder('struct_folder')
        self.assertTrue(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithNonStructuralFolder(self):
        f = dummy.NonStructuralFolder('ns_folder')
        self.assertFalse(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsDefaultPageInFolder(self):
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertFalse(view.isDefaultPageInFolder())
        self.assertTrue(self.folder.canSetDefaultPage())
        self.folder.setDefaultPage('test')
        # re-create the view, because the old value is cached
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertTrue(view.isDefaultPageInFolder())

    def testNavigationRootPath(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootPath(),
                         self.portal.portal_url.getPortalPath())

    def testNavigationRootUrl(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootUrl(), self.portal.absolute_url())

    def testGetParentObject(self):
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertEqual(view.getParentObject(), self.folder)
        # Make sure this looks only at containment
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test.__of__(self.portal), self.app.REQUEST)
        self.assertEqual(view.getParentObject(), self.folder)

    def testIsFolderOrFolderDefaultPage(self):
        # an actual folder whould return true
        view = Plone(self.folder, self.app.REQUEST)
        self.assertTrue(view.isFolderOrFolderDefaultPage())
        # But not a document
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertFalse(view.isFolderOrFolderDefaultPage())
        # Unless we make it the default view
        self.folder.setDefaultPage('test')
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertTrue(view.isFolderOrFolderDefaultPage())
        # And if we have a non-structural folder it should not be true
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.ns_folder, self.app.REQUEST)
        self.assertFalse(view.isFolderOrFolderDefaultPage())

    def testIsPortalOrPortalDefaultPage(self):
        # an actual folder whould return true
        view = Plone(self.portal, self.app.REQUEST)
        self.assertTrue(view.isPortalOrPortalDefaultPage())
        # But not a document
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'portal_test',
                                  title='Test default page')
        self._invalidateRequestMemoizations()
        view = Plone(self.portal.portal_test, self.app.REQUEST)
        self.assertFalse(view.isPortalOrPortalDefaultPage())
        # Unless we make it the default view
        self.portal.setDefaultPage('portal_test')
        self._invalidateRequestMemoizations()
        view = Plone(self.portal.portal_test, self.app.REQUEST)
        self.assertTrue(view.isPortalOrPortalDefaultPage())

    def testGetCurrentFolder(self):
        # If context is a folder, then the folder is returned
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)

        # If context is not a folder, then the parent is returned
        # A bit crude ... we need to make sure our memos don't stick in the
        # tests
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)

        # The real container is returned regardless of context
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test.__of__(self.portal), self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)

        # A non-structural folder does not count as a folder`
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.ns_folder, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)

        # And even a structural folder that is used as a default page
        # returns its parent
        self.folder.setDefaultPage('ns_folder')
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.ns_folder, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)

    def testCropText(self):
        view = Plone(self.portal, self.app.REQUEST)
        self.assertEqual(view.cropText(b'Hello world', 7), b'Hello ...')
        self.assertEqual(view.cropText('Hello world', 7), 'Hello ...')
        self.assertEqual(view.cropText(b'Hello world', 10), b'Hello worl...')
        self.assertEqual(view.cropText('Hello world', 10), 'Hello worl...')
        self.assertEqual(view.cropText(b'Hello world', 99), b'Hello world')
        self.assertEqual(view.cropText('Hello world', 99), 'Hello world')
        self.assertEqual(
            view.cropText('Koko\u0159\xedn', 5), 'Koko\u0159...')
        # Test utf encoded string Kokorin with 'r' and 'i' accented
        # Must return 6 characters, because 5th character is two byte
        text = 'Koko\u0159\xedn'.encode()
        self.assertEqual(view.cropText(text, 5), b'Koko\xc5\x99...')

    def testSiteEncoding(self):
        view = Plone(self.portal, self.app.REQUEST)
        self.assertEqual('utf-8', view.site_encoding())

    def test_human_readable_size(self):
        view = Plone(self.portal, self.app.REQUEST)
        from Products.CMFPlone.utils import human_readable_size
        self.assertIs(view.human_readable_size, human_readable_size)
