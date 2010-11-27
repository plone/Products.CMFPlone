from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from Products.CMFPlone.browser.ploneview import Plone


class TestPloneView(PloneTestCase.PloneTestCase):
    """Tests the global plone view."""

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
        self.assertEquals(value, 'Mar 09, 1997 01:45 PM')

    def testIsStructuralFolderWithNonFolder(self):
        i = dummy.Item()
        self.failIf(Plone(i, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithFolder(self):
        f = dummy.Folder('struct_folder')
        self.failUnless(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsStructuralFolderWithNonStructuralFolder(self):
        f = dummy.NonStructuralFolder('ns_folder')
        self.failIf(Plone(f, self.app.REQUEST).isStructuralFolder())

    def testIsDefaultPageInFolder(self):
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failIf(view.isDefaultPageInFolder())
        self.failUnless(self.folder.canSelectDefaultPage())
        self.folder.saveDefaultPage('test')
        # re-create the view, because the old value is cached
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failUnless(view.isDefaultPageInFolder())

    def testNavigationRootPath(self):
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.navigationRootPath(), self.portal.portal_url.getPortalPath())

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
        self.failUnless(view.isFolderOrFolderDefaultPage())
        # But not a document
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failIf(view.isFolderOrFolderDefaultPage())
        # Unless we make it the default view
        self.folder.saveDefaultPage('test')
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.test, self.app.REQUEST)
        self.failUnless(view.isFolderOrFolderDefaultPage())
        # And if we have a non-structural folder it should not be true
        f = dummy.NonStructuralFolder('ns_folder')
        self.folder._setObject('ns_folder', f)
        self._invalidateRequestMemoizations()
        view = Plone(self.folder.ns_folder, self.app.REQUEST)
        self.failIf(view.isFolderOrFolderDefaultPage())

    def testIsPortalOrPortalDefaultPage(self):
        # an actual folder whould return true
        view = Plone(self.portal, self.app.REQUEST)
        self.failUnless(view.isPortalOrPortalDefaultPage())
        # But not a document
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', 'portal_test',
                                  title='Test default page')
        self._invalidateRequestMemoizations()
        view = Plone(self.portal.portal_test, self.app.REQUEST)
        self.failIf(view.isPortalOrPortalDefaultPage())
        # Unless we make it the default view
        self.portal.saveDefaultPage('portal_test')
        self._invalidateRequestMemoizations()
        view = Plone(self.portal.portal_test, self.app.REQUEST)
        self.failUnless(view.isPortalOrPortalDefaultPage())

    def testGetCurrentFolder(self):
        # If context is a folder, then the folder is returned
        view = Plone(self.folder, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)

        # If context is not a folder, then the parent is returned
        # A bit crude ... we need to make sure our memos don't stick in the tests
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
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Topic', 'topic')

        self._invalidateRequestMemoizations()
        view = Plone(self.folder.topic, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder.topic)
        self.folder.saveDefaultPage('topic')

        self._invalidateRequestMemoizations()
        view = Plone(self.folder.topic, self.app.REQUEST)
        self.assertEqual(view.getCurrentFolder(), self.folder)

    def testCropText(self):
        view = Plone(self.portal, self.app.REQUEST)
        self.assertEqual(view.cropText('Hello world', 7), 'Hello ...')
        self.assertEqual(view.cropText('Hello world', 99), 'Hello world')
        self.assertEqual(view.cropText('Hello world', 10), 'Hello worl...')
        self.assertEqual(view.cropText(u'Hello world', 10), u'Hello worl...')
        self.assertEqual(view.cropText(u'Koko\u0159\xedn', 5), u'Koko\u0159...')
        # Test utf encoded string Kokorin with 'r' and 'i' accented
        # Must return 6 characters, because 5th character is two byte
        text = u'Koko\u0159\xedn'.encode('utf8')
        self.assertEqual(view.cropText(text, 5), 'Koko\xc5\x99...')

    def testSiteEncoding(self):
        view = Plone(self.portal, self.app.REQUEST)
        self.assertEqual('utf-8', view.site_encoding())


class TestVisibleIdsEnabled(PloneTestCase.PloneTestCase):
    '''Tests the visibleIdsEnabled method'''

    def afterSetUp(self):
        self.view = Plone(self.portal, self.app.REQUEST)
        self.member = self.portal.portal_membership.getAuthenticatedMember()
        self.props = self.portal.portal_properties.site_properties

    def testFailsWithSitePropertyDisabled(self):
        # Set baseline
        self.member.setProperties(visible_ids=False)
        self.props.manage_changeProperties(visible_ids=False)
        # Should fail when site property is set false
        self.failIf(self.view.visibleIdsEnabled())
        self.member.setProperties(visible_ids=True)
        self.failIf(self.view.visibleIdsEnabled())

    def testFailsWithMemberPropertyDisabled(self):
        # Should fail when member property is false
        self.member.setProperties(visible_ids=False)
        self.props.manage_changeProperties(visible_ids=True)
        self.failIf(self.view.visibleIdsEnabled())

    def testSucceedsWithMemberAndSitePropertyEnabled(self):
        # Should succeed only when site property and member property are true
        self.props.manage_changeProperties(visible_ids=True)
        self.member.setProperties(visible_ids=True)
        self.failUnless(self.view.visibleIdsEnabled())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPloneView))
    suite.addTest(makeSuite(TestVisibleIdsEnabled))
    return suite
