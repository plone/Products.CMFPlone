# -*- coding: utf-8 -*-
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.app.layout.viewlets.common import ContentViewsViewlet
from plone.app.layout.viewlets.common import GlobalSectionsViewlet
from plone.app.layout.viewlets.common import LogoViewlet
from plone.app.layout.viewlets.common import TitleViewlet
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.protect import authenticator as auth
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.interfaces import ISiteSchema
from zope.component import getUtility
from zope.component.hooks import setSite
from zope.interface import alsoProvides
from zope.interface import directlyProvides
from zope.interface import noLongerProvides


# Red pixel with filename pixel.png
SITE_LOGO_BASE64 = b'filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgA'\
                   b'AAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAA'\
                   b'AAElFTkSuQmCC'


class TestViewletBase(ViewletsTestCase):
    """Test the base class for the viewlets.
    """

    def test_update(self):
        request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.portal.invokeFactory('Folder', 'f1')
        context = getattr(self.portal, 'f1')
        alsoProvides(context, INavigationRoot)
        viewlet = ViewletBase(context, request, None, None)
        viewlet.update()
        self.assertEqual(viewlet.site_url, "http://nohost/plone")
        self.assertEqual(viewlet.navigation_root_url, "http://nohost/plone/f1")


class TestContentViewsViewlet(ViewletsTestCase):
    """Test the content views viewlet.
    """

    def setUp(self):
        super(TestContentViewsViewlet, self).setUp()
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        self.folder.title = u"Folder"

    def _invalidateRequestMemoizations(self):
        try:
            del self.app.REQUEST.__annotations__
        except AttributeError:
            pass

    def test_set1_on_portal_root(self):
        self._invalidateRequestMemoizations()
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.app.REQUEST['ACTUAL_URL'] = self.portal.absolute_url()
        view = ContentViewsViewlet(self.portal, self.app.REQUEST, None)
        view.update()
        self.assertEqual(view.tabSet1[0]['id'], 'folderContents')

    def test_set1_NonStructuralFolder(self):
        self._invalidateRequestMemoizations()
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.app.REQUEST['ACTUAL_URL'] = self.folder.absolute_url()
        directlyProvides(self.folder, INonStructuralFolder)
        view = ContentViewsViewlet(self.folder, self.app.REQUEST, None)
        view.update()
        noLongerProvides(self.folder, INonStructuralFolder)
        self.assertEqual(1, len([t for t in view.tabSet1 if t[
                         'id'] == 'folderContents']))

    def test_set1(self):
        self._invalidateRequestMemoizations()
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.app.REQUEST['ACTUAL_URL'] = '%s/edit?_authenticator=%s' % (
            self.folder.test.absolute_url(),
            auth.createToken()
        )
        view = ContentViewsViewlet(self.folder.test, self.app.REQUEST, None)
        view.update()
        self.assertEqual(
            1, len([t for t in view.tabSet1 if t['id'] == 'folderContents']))
        self.assertEqual(
            ['edit'], [t['id'] for t in view.tabSet1 if t['selected']])


class TestTitleViewsViewlet(ViewletsTestCase):
    """Test the title viewlet.
    """

    def setUp(self):
        super(TestTitleViewsViewlet, self).setUp()
        self.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        self.folder.title = u"Folder"

    def _invalidateRequestMemoizations(self):
        try:
            del self.app.REQUEST.__annotations__
        except AttributeError:
            pass

    def test_title_viewlet_on_portal(self):
        """Title viewlet renders navigation root title
        """
        self._invalidateRequestMemoizations()
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.app.REQUEST['ACTUAL_URL'] = self.portal.absolute_url()
        viewlet = TitleViewlet(self.portal, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(viewlet.site_title, 'Plone site')
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema, prefix='plone', check=False)
        site_settings.site_title = u'Süper Site'
        self._invalidateRequestMemoizations()
        viewlet.update()
        self.assertEqual(viewlet.site_title, u'S\xfcper Site')

    def test_title_viewlet_on_content(self):
        """Title viewlet renders navigation root title
        """
        self._invalidateRequestMemoizations()
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.app.REQUEST['ACTUAL_URL'] = self.folder.test.absolute_url()
        viewlet = TitleViewlet(self.folder.test, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(viewlet.site_title,
                         'Test default page &mdash; Plone site')
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema, prefix="plone", check=False)
        site_settings.site_title = u'Süper Site'
        self._invalidateRequestMemoizations()
        viewlet.update()
        self.assertEqual(viewlet.site_title,
                         u'Test default page &mdash; S\xfcper Site')

    def test_title_viewlet_with_navigation_root(self):
        """Title viewlet renders navigation root title
        """
        self._invalidateRequestMemoizations()
        setRoles(self.portal, TEST_USER_ID, ['Manager', 'Member'])
        self.app.REQUEST['ACTUAL_URL'] = self.folder.test.absolute_url()
        directlyProvides(self.folder, INavigationRoot)
        viewlet = TitleViewlet(self.folder.test, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(viewlet.site_title,
                         u'Test default page &mdash; Folder')


class TestLogoViewlet(ViewletsTestCase):
    """Test the site logo viewlet.
    """

    def _set_site(self, context):
        """Set context as a site.
        """
        # Set the portal's getSiteManager method on context.
        # This is a hackish way to make setSite work without creating a site
        # with five.localsitemanager.
        # ATTENTION: this works only for the purpose of this test.
        context.getSiteManager = self.portal.getSiteManager
        setSite(context)

    def test_logo_viewlet_portal_root_default(self):
        """When no logo is set, and viewlet is opened on a non-navigation root,
        obtain the default one from the portal.
        """
        viewlet = LogoViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(
            viewlet.img_src, '{0}/logo.png'.format(self.portal.absolute_url()))

    def test_logo_viewlet_portal_root_registry(self):
        """When a logo is set, and viewlet is opened on a non-navigation root,
        obtain the registry logo from the portal.
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        settings.site_logo = SITE_LOGO_BASE64

        viewlet = LogoViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(
            viewlet.img_src,
            '{0}/@@site-logo/pixel.png'.format(self.portal.absolute_url())
        )

    def test_logo_viewlet_navigation_root_default(self):
        """When no logo is set, and viewlet is opened on a navigation root,
        obtain the default one from the navigation root.
        """
        self._set_site(self.folder)
        viewlet = LogoViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertEqual(
            viewlet.img_src, '{0}/logo.png'.format(self.folder.absolute_url()))

    def test_viewlet_navigation_root_registry(self):
        """When a logo is set, and viewlet is opened on a navigation root,
        obtain the registry logo from the navigation root.
        """
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        settings.site_logo = SITE_LOGO_BASE64

        # Set fake site after registry setup...
        self._set_site(self.folder)
        viewlet = LogoViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(
            viewlet.img_src,
            '{0}/@@site-logo/pixel.png'.format(self.folder.absolute_url())
        )


class TestGlobalSectionsViewlet(ViewletsTestCase):
    """Test the global sections views viewlet.
    """

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.registry = getUtility(IRegistry)
        self.folder = self.portal['Members'][TEST_USER_ID]
        self.portal.Members.reindexObject()
        self.folder.reindexObject()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def _get_navtree(self):
        gsv = GlobalSectionsViewlet(self.portal, self.request.clone(), None)
        return gsv.navtree

    def test_selectedtabs(self):
        """ Test selected tabs the simplest case
        """
        request = self.layer['request']
        request['URL'] = self.folder.absolute_url()
        gsv = GlobalSectionsViewlet(self.folder, request, None)
        gsv.update()
        self.assertEqual(gsv.selected_tabs, {'portal': 'Members'})
        self.assertEqual(gsv.selected_portal_tab, 'Members')

    def test_selectedtabs_navroot(self):
        """ Test selected tabs with a INavigationroot folder involved
        """
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'navroot', title='My new root')
        navroot = self.portal['navroot']
        alsoProvides(navroot, INavigationRoot)
        navroot.invokeFactory('Folder', 'abc', title='short')
        navroot.invokeFactory('Folder',
                              'xyz',
                              title='Folder with a looong name')
        request = self.layer['request']
        request['URL'] = navroot['abc'].absolute_url()
        gsv = GlobalSectionsViewlet(navroot, request, None)
        gsv.update()
        self.assertEqual(gsv.selected_tabs, {'portal': 'abc'})
        self.assertEqual(gsv.selected_portal_tab, 'abc')

    def test_globalnav_respects_types_use_view_action_in_listings(self):
        """ Test selected tabs with a INavigationroot folder involved
        """
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Image', 'image', title=u'Söme Image')
        self.portal.invokeFactory('File', 'file', title=u'Some File')
        self.portal.invokeFactory('Document', 'doc', title=u'Some Döcument')
        request = self.layer['request']
        gsv = GlobalSectionsViewlet(self.portal, request, None)
        gsv.update()
        html = gsv.render()
        self.assertIn('href="http://nohost/plone/image/view"', html)
        self.assertIn('href="http://nohost/plone/file/view"', html)
        self.assertIn('href="http://nohost/plone/doc"', html)

    def test_globalnav_navigation_depth(self):
        """ Test selected tabs with a INavigationroot folder involved
        """
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        registry = getUtility(IRegistry)
        registry['plone.navigation_depth'] = 3
        self.portal.invokeFactory('Folder', 'folder', title=u'Földer')
        self.portal.invokeFactory('Folder', 'folder2', title=u'Folder 2')
        self.portal.invokeFactory('Folder', 'folder3', title=u'Folder 3')
        folder = self.portal.folder
        folder.invokeFactory('Folder', 'subfolder', title=u'Subfolder')
        folder.invokeFactory('Folder', 'subfolder2', title=u'Sübfolder 2')
        subfolder = folder.subfolder
        subfolder.invokeFactory('Folder', 'subsubfolder', title=u'Sub2folder')

        request = self.layer['request']
        navtree = self._get_navtree()
        self.assertListEqual(
            sorted(navtree),
            [
                '/plone',
                '/plone/Members',
                '/plone/folder',
                '/plone/folder/subfolder'
            ],
        )
        self.assertListEqual(
            [x['title'] for x in navtree['/plone']],
            [u'Home', u'Members', u'Földer', u'Folder 2', u'Folder 3'],
        )
        self.assertListEqual(
            [x['title'] for x in navtree['/plone/folder']],
            [u'Subfolder', u'Sübfolder 2'],
        )
        self.assertListEqual(
            [x['title'] for x in navtree['/plone/folder/subfolder']],
            [u'Sub2folder'],
        )

        gsv = GlobalSectionsViewlet(self.portal, request, None)
        gsv.update()
        self.assertTrue(gsv.render())

    def test_default_settings(self):
        self.assertEqual(self.registry['plone.navigation_depth'], 3)
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone', '/plone/Members'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members'],
        )

    def test_do_not_generate_tabs(self):
        self.registry['plone.generate_tabs'] = False
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html'],
        )

    def test_generate_tabs_non_folderish(self):
        self.registry['plone.nonfolderish_tabs'] = False
        self.portal.invokeFactory(
            'Document',
            'test-doc',
            title=u'A simple document (àèìòù)',
        )
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone', '/plone/Members'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members'],
        )

    def test_generate_tabs_sorted(self):
        self.portal.invokeFactory(
            'Document',
            'test-doc-2',
            title=u'Document 2',
        )
        self.portal.invokeFactory(
            'Document',
            'test-doc-1',
            title=u'Document 1',
        )
        navtree = self._get_navtree()
        # default sorting by position in parent
        self.assertListEqual(sorted(navtree), ['/plone', '/plone/Members'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
                '/plone/Members',
                '/plone/test-doc-2',
                '/plone/test-doc-1',
            ],
        )

        # check we can sort by title
        self.registry['plone.sort_tabs_on'] = u'sortable_title'
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone', '/plone/Members'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
                '/plone/Members',
                '/plone/test-doc-1',
                '/plone/test-doc-2',
            ],
        )

        # check we can reverse sorting
        self.registry['plone.sort_tabs_reversed'] = True
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone', '/plone/Members'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
                '/plone/test-doc-2',
                '/plone/test-doc-1',
                '/plone/Members',
            ],
        )

    def test_generate_tabs_displayed_types(self):
        self.registry['plone.displayed_types'] = (
            u'Image',
            u'File',
            u'Link',
            u'News Item',
            u'Document',
            u'Event',
        )
        navtree = self._get_navtree()
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
            ],
        )

    def test_generate_tabs_filter_on_state(self):
        self.registry['plone.filter_on_workflow'] = True
        navtree = self._get_navtree()
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
            ],
        )
        self.registry['plone.workflow_states_to_show'] = (u'private', )
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone', '/plone/Members'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members'],
        )

        # Let's check this works also with deep navigation
        self.registry['plone.navigation_depth'] = 2
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone', '/plone/Members'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone/Members']],
            ['/plone/Members/test_user_1_'],
        )

    def test_generate_tabs_exclude_from_nav(self):
        self.portal.invokeFactory(
            'Folder',
            'test-folder',
            title=u'Test folder',
        )
        self.portal.invokeFactory(
            'Folder',
            'excluded-folder',
            title=u'Excluded folder',
            exclude_from_nav=True,
        )
        self.portal['excluded-folder'].invokeFactory(
            'Folder',
            'sub-folder',
            title=u'Sub folder',
        )

        navtree = self._get_navtree()
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            [
                '/plone/index_html',
                '/plone/Members',
                '/plone/test-folder',
                '/plone/excluded-folder',
            ],
        )

        # Check also that we we have proper nesting
        self.registry['plone.navigation_depth'] = 2
        navtree = self._get_navtree()
        self.assertListEqual(
            sorted(navtree),
            ['/plone', '/plone/Members', '/plone/excluded-folder'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone/excluded-folder']],
            ['/plone/excluded-folder/sub-folder'],
        )

        self.registry['plone.navigation_depth'] = 1
        self.registry['plone.show_excluded_items'] = False
        navtree = self._get_navtree()
        self.assertListEqual(sorted(navtree), ['/plone'])
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members', '/plone/test-folder'],
        )

        # If we increase the navigation depth to 2 the sub folder in the
        # exclude folder it is there but unlinked
        self.registry['plone.navigation_depth'] = 2
        navtree = self._get_navtree()
        self.assertListEqual(
            sorted(navtree),
            ['/plone', '/plone/Members', '/plone/excluded-folder'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members', '/plone/test-folder'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone/excluded-folder']],
            ['/plone/excluded-folder/sub-folder'],
        )

        self.portal['excluded-folder']['sub-folder'].exclude_from_nav = True
        self.portal['excluded-folder']['sub-folder'].reindexObject()
        navtree = self._get_navtree()
        self.assertListEqual(
            sorted(navtree),
            ['/plone', '/plone/Members'],
        )
        self.assertListEqual(
            [item['path'] for item in navtree['/plone']],
            ['/plone/index_html', '/plone/Members', '/plone/test-folder'],
        )
