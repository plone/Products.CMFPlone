from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.interfaces import ISearchSchema

from gzip import GzipFile
from StringIO import StringIO

from DateTime import DateTime
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.publisher.interfaces import INotFound

from plone.app.layout.navigation.interfaces import INavigationRoot

from Products.CMFCore.utils import getToolByName

from plone.app.testing.bbb import PloneTestCase


class SiteMapTestCase(PloneTestCase):
    """base test case with convenience methods for all sitemap tests"""

    def afterSetUp(self):
        super(SiteMapTestCase, self).afterSetUp()
        registry = getUtility(IRegistry)
        self.site_settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.site_settings.enable_sitemap = True
        self.sitemap = getMultiAdapter((self.portal, self.portal.REQUEST),
                                       name='sitemap.xml.gz')
        self.wftool = getToolByName(self.portal, 'portal_workflow')

        # we need to explizitly set a workflow cause we can't rely on the
        # test environment.
        # `instance test -m plone.app.layout`:
        # wftool._default_chain == 'simple_publication_workflow'
        # `instance test -m plone.app`:
        # wftool._default_chain == 'plone_workflow'
        self.wftool.setChainForPortalTypes(['Document'],
                                           'simple_publication_workflow')

        self.site_properties = getToolByName(
            self.portal, 'portal_properties').site_properties

        # setup private content that isn't accessible for anonymous
        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='private', type_name='Document')
        private = self.portal.private
        self.assertTrue('private' == self.wftool.getInfoFor(private,
                                                            'review_state'))

        # setup published content that is accessible for anonymous
        self.portal.invokeFactory(id='published', type_name='Document')
        published = self.portal.published
        self.wftool.doActionFor(published, 'publish')
        self.assertTrue('published' == self.wftool.getInfoFor(published,
                                                              'review_state'))

        # setup pending content that isn't accessible for anonymous
        self.portal.invokeFactory(id='pending', type_name='Document')
        pending = self.portal.pending
        self.wftool.doActionFor(pending, 'submit')
        self.assertTrue('pending' == self.wftool.getInfoFor(pending,
                                                            'review_state'))
        self.logout()

    def uncompress(self, sitemapdata):
        sio = StringIO(sitemapdata)
        unziped = GzipFile(fileobj=sio)
        xml = unziped.read()
        unziped.close()
        return xml

    def test_disabled(self):
        '''
        If the sitemap is disabled throws a 404 error.
        '''
        self.site_settings.enable_sitemap = False
        try:
            self.sitemap()
        except Exception, e:
            # zope2 and repoze.zope2 use different publishers and raise
            # different exceptions. but both implement INotFound.
            self.assertTrue(INotFound.providedBy(e))
        else:
            self.fail('The disabled sitemap view has to raise NotFound!')

    def test_authenticated_before_anonymous(self):
        '''
        Requests for the sitemap by authenticated users are not cached.
        anomymous users get a uncached sitemap that only contains content
        that they are supposed to see.
        '''

        # first round as an authenticated (manager)
        self.loginAsPortalOwner()
        xml = self.uncompress(self.sitemap())
        self.assertTrue('<loc>http://nohost/plone/private</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/pending</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/published</loc>' in xml)

        # second round as anonymous
        self.logout()
        xml = self.uncompress(self.sitemap())
        self.assertFalse('<loc>http://nohost/plone/private</loc>' in xml)
        self.assertFalse('<loc>http://nohost/plone/pending</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/published</loc>' in xml)

    def test_anonymous_before_authenticated(self):
        '''
        Requests for the sitemap by anonymous users are cached.
        authenticated users get a uncached sitemap. Test that the cached
        Sitemap is not delivered to authenticated users.
        '''

        # first round as anonymous
        xml = self.uncompress(self.sitemap())
        self.assertFalse('<loc>http://nohost/plone/private</loc>' in xml)
        self.assertFalse('<loc>http://nohost/plone/pending</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/published</loc>' in xml)

        # second round as an authenticated (manager)
        self.loginAsPortalOwner()
        xml = self.uncompress(self.sitemap())
        self.assertTrue('<loc>http://nohost/plone/private</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/pending</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/published</loc>' in xml)

    def test_changed_catalog(self):
        '''
        The sitemap is generated from the catalog. If the catalog changes, a
        new sitemap has to be generated.
        '''

        xml = self.uncompress(self.sitemap())
        self.assertFalse('<loc>http://nohost/plone/pending</loc>' in xml)

        # changing the workflow state
        self.loginAsPortalOwner()
        pending = self.portal.pending
        self.wftool.doActionFor(pending, 'publish')
        self.logout()

        xml = self.uncompress(self.sitemap())
        self.assertTrue('<loc>http://nohost/plone/pending</loc>' in xml)

        # removing content
        self.loginAsPortalOwner()
        self.portal.manage_delObjects(['published', ])
        self.logout()

        xml = self.uncompress(self.sitemap())
        self.assertFalse('<loc>http://nohost/plone/published</loc>' in xml)

    def test_navroot(self):
        '''
        Sitemap generated from an INavigationRoot
        '''
        # setup navroot content that is accessible for anonymous
        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='navroot', type_name='Folder')
        navroot = self.portal.navroot
        self.wftool.doActionFor(navroot, 'publish')
        self.assertTrue('published' == self.wftool.getInfoFor(
            navroot, 'review_state'))
        alsoProvides(navroot, INavigationRoot)
        navroot.invokeFactory(id='published', type_name='Document')
        published = navroot.published
        self.wftool.doActionFor(published, 'publish')
        self.assertTrue('published' == self.wftool.getInfoFor(
            published, 'review_state'))
        self.logout()

        sitemap = getMultiAdapter((self.portal.navroot, self.portal.REQUEST),
                                  name='sitemap.xml.gz')
        xml = self.uncompress(sitemap())
        self.assertFalse('<loc>http://nohost/plone/published</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/navroot</loc>' in xml)
        self.assertTrue(
            '<loc>http://nohost/plone/navroot/published</loc>' in xml)

    def test_types_not_searched(self):
        '''
        Test that types_not_searched is respected
        '''
        # Set News Items not to be searchable (more likely Images)
        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='newsitem', type_name='News Item')
        newsitem = self.portal.newsitem
        self.wftool.doActionFor(newsitem, 'publish')
        self.assertTrue('published' == self.wftool.getInfoFor(
            newsitem, 'review_state'))
        registry = getUtility(IRegistry)
        search_settings = registry.forInterface(ISearchSchema, prefix="plone")
        search_settings.types_not_searched = ('News Item',)
        self.logout()

        xml = self.uncompress(self.sitemap())
        self.assertFalse('<loc>http://nohost/plone/newsitem</loc>' in xml)

    def test_typesUseViewActionInListings(self):
        '''
        Test that typesUseViewActionInListings is respected
        '''
        # Set News Items not to be searchable (more likely Images)
        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='newsitem', type_name='News Item')
        newsitem = self.portal.newsitem
        self.wftool.doActionFor(newsitem, 'publish')
        self.assertTrue('published' == self.wftool.getInfoFor(
            newsitem, 'review_state'))
        registry = getUtility(IRegistry)
        registry['plone.types_use_view_action_in_listings'] = [u'News Item']

        self.logout()

        xml = self.uncompress(self.sitemap())
        self.assertTrue('<loc>http://nohost/plone/newsitem/view</loc>' in xml)

    def test_default_pages(self):
        '''
        Default pages should show up at their parent's url with the greater of
        their or their parent's modification time.
        '''

        self.loginAsPortalOwner()
        self.portal.invokeFactory(id='folder', type_name='Folder')
        folder = self.portal.folder
        folder.default_page = "default"
        self.wftool.doActionFor(folder, 'publish')
        self.assertTrue('published' == self.wftool.getInfoFor(
            folder, 'review_state'))

        folder.invokeFactory(id='default', type_name='Document')
        default = folder.default
        self.wftool.doActionFor(default, 'publish')
        self.assertTrue('published' == self.wftool.getInfoFor(
            default, 'review_state'))
        self.assertTrue(self.portal.plone_utils.isDefaultPage(default))

        default.modification_date = DateTime("2001-01-01")
        folder.modification_date = DateTime("2000-01-01")
        self.portal.portal_catalog.reindexObject(folder)
        self.portal.portal_catalog.reindexObject(default)
        self.portal.default_page = "published"
        self.portal.portal_catalog.reindexObject(self.portal.published)
        self.logout()

        xml = self.uncompress(self.sitemap())
        self.assertFalse(
            '<loc>http://nohost/plone/folder/default</loc>' in xml)
        self.assertTrue('<loc>http://nohost/plone/folder</loc>' in xml)
        self.assertTrue('<lastmod>2001-01-01T' in xml)
        self.assertTrue('<loc>http://nohost/plone</loc>' in xml)
        self.assertFalse('<loc>http://nohost/plone/published</loc>' in xml)
