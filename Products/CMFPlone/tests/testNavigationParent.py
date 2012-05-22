# Tests the navigationParent script

from Products.CMFPlone.tests import PloneTestCase


class TestNavigationParent(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('Folder', 'f1', title='Folder 1')
        self.f1 = getattr(self.folder, 'f1')
        self.f1.invokeFactory('Folder', 'f2', title='Folder 2')
        self.f2 = getattr(self.f1, 'f2')

    def testPortalRoot(self):
        self.assertTrue(self.portal.navigationParent() is None)

    def testFolderInPortal(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'pf', title='portal folder')
        pf = getattr(self.portal, 'pf')
        self.assertEqual(pf.navigationParent(), self.portal.absolute_url())

    def testFolderInFolder(self):
        self.assertEqual(self.f2.navigationParent(), self.f1.absolute_url())

    def testDocumentInFolder(self):
        self.f1.invokeFactory('Document', 'd1', title='Document 1')
        d1 = getattr(self.f1, 'd1')
        self.assertEqual(d1.navigationParent(), self.f1.absolute_url())

    # Standard behaviour for default_page/index_html - go up two levels,
    # since going to parent will just end you up at the same object again

    def testIndexHtmlInFolder(self):
        self.f2.invokeFactory('Document', 'index_html', title='Document 1')
        d1 = getattr(self.f2, 'index_html')
        self.assertEqual(d1.navigationParent(), self.f1.absolute_url())

    def testDefaultPageInFolder(self):
        self.f2.invokeFactory('Document', 'd1', title='Document 1')
        d1 = getattr(self.f2, 'd1')
        self.f2.setDefaultPage('d1')
        self.assertEqual(d1.navigationParent(), self.f1.absolute_url())

    def testFolderishIndexHtmlInFolder(self):
        self.f2.invokeFactory('Folder', 'index_html', title='Index folder')
        ih = getattr(self.f2, 'index_html')
        self.assertEqual(ih.navigationParent(), self.f1.absolute_url())

    def testFolderishDefaultPageInFolder(self):
        self.f1.setDefaultPage('f2')
        self.assertEqual(self.f2.navigationParent(),
                         self.folder.absolute_url())

    # Optional behaviour - don't fall through, go straight to parent.
    # This is what we do on folder_contents, for example. It's only sensible
    # if you intend to link/redirect to an object + a page template

    def testNoFallThroughIndexHtmlInFolder(self):
        self.f2.invokeFactory('Document', 'index_html', title='Document 1')
        d1 = getattr(self.f2, 'index_html')
        self.assertEqual(d1.navigationParent(fallThroughDefaultPage=False),
                            self.f2.absolute_url())

    def testNoFallThroughDefaultPageInFolder(self):
        self.f2.invokeFactory('Document', 'd1', title='Document 1')
        d1 = getattr(self.f2, 'd1')
        self.f2.setDefaultPage('d1')
        self.assertEqual(d1.navigationParent(fallThroughDefaultPage=False),
                            self.f2.absolute_url())

    def testNoFallThroughFolderishIndexHtmlInFolder(self):
        self.f2.invokeFactory('Folder', 'index_html', title='Index folder')
        ih = getattr(self.f2, 'index_html')
        self.assertEqual(ih.navigationParent(fallThroughDefaultPage=False),
                            self.f2.absolute_url())

    def testNoFallThroughFolderishDefaultPageInFolder(self):
        self.f1.setDefaultPage('f2')
        self.assertEqual(self.f2.navigationParent(
                            fallThroughDefaultPage=False),
                            self.f1.absolute_url())

    # Very special case - if you have an index_html inside an index_html...
    def testRecursiveDefaultPage(self):
        self.f1.setDefaultPage('f2')
        self.f2.invokeFactory('Folder', 'index_html',
                              title='index index index')
        ih = getattr(self.f2, 'index_html')
        self.assertEqual(ih.navigationParent(), self.folder.absolute_url())

    # Permission checks on parent

    def testNoParentViewPermission(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'pf', title='portal folder')
        pf = getattr(self.portal, 'pf')
        pf.invokeFactory('Folder', 'lf', title='listable folder')
        lf = getattr(pf, 'lf')
        pf.manage_permission('List folder contents', ['Manager'], 0)
        pf.manage_permission('View', ['Manager'], 0)
        lf.manage_permission('List folder contents',
                             ['Member', 'Manager', 'Owner'], 0)
        lf.manage_permission('View', ['Member', 'Manager', 'Owner'], 0)
        self.setRoles(['Member'])

        self.assertTrue(lf.navigationParent() is None)

    def testNoParentListPermissions(self):
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Folder', 'pf', title='portal folder')
        pf = getattr(self.portal, 'pf')
        pf.invokeFactory('Folder', 'lf', title='listable folder')
        lf = getattr(pf, 'lf')
        pf.manage_permission('List folder contents', ['Manager'], 0)
        lf.manage_permission('List folder contents',
                             ['Member', 'Manager', 'Owner'], 0)
        self.setRoles(['Member'])

        self.assertTrue(lf.navigationParent(
                checkPermissions=['List folder contents']) is None)
